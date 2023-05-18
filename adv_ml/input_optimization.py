# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/input_optimization.ipynb.

# %% auto 0
__all__ = ['PerturbationCallback', 'InputOptimizer']

# %% ../nbs/input_optimization.ipynb 4
from typing import Type
from abc import ABC, abstractmethod

from torch import nn
from fastai.vision.all import *


class PerturbationCallback(ABC, Callback):
    "Manages the input perturbation for an `InputOptimizer`"
    @abstractmethod
    def init_pert(self, x):
        ...
    

class _Perturbation(nn.Module):
    def __init__(self, p):
        super().__init__()
        self.p = p
        
    def forward(self, x):
        return x + self.p

                
class _TrainLoop(TrainEvalCallback):
    def before_train(self):
        super().before_train()
        self.model.eval()

    def before_validate(self):
        raise CancelValidException


class InputOptimizer(object):
    "Constructs adversarial examples: slightly perturbed inputs that fool classification models"
    def __init__(self,
                 model: Module,
                 pert_cb: Type[PerturbationCallback],
                 loss: Callable = CrossEntropyLossFlat(),
                 lr: float = None,  # pass `None` to try pick `lr` based on other parameters
                 targeted: bool = False,  # Whether the constructed inputs should be classified as the specified targets or not
                 min_delta: float = 1e-2,  # Minimum loss delta for `ReduceLROnPlateau` and `EarlyStoppingCallback`
                 min_lr: float = 1e-6,  # Minimum lr for `ReduceLROnPlateau`
                 # defaults taken from advertorch
                 epoch_size: int = 10,  # Affects how often epoch-callbacks are called (e.g. `Recorder`` and `EarlyStoppingCallback`)
                 n_epochs: int = 4):
        self.loss = loss if targeted else (lambda *args, **kwargs: -loss(*args, **kwargs))
        store_attr('model, pert_cb, lr, min_delta, min_lr, epoch_size, n_epochs')
        
        if self.lr is None:
            assert hasattr(pert_cb, 'epsilon'), "Can't pick lr for if the callback isn't based on an epsilon"
            self.lr = pert_cb.epsilon / self.epoch_size

        self.model.eval()
        self.model.requires_grad_(False)

    def perturb(self, dsets):
        x, y = dsets.load()
        x, y = x.detach().clone(), y.detach().clone()  # TODO: can I get rid of this?

        x_hat = self._perturb(x, y)

        return Datasets(tls=[TfmdLists(x_hat, ToTensor()),  # ToTensor for decoding
                             dsets.tls[1]])

    def _perturb(self, x, y):
        self.pert_cb.init_pert(x)

        learner = Learner(DataLoaders([(x, y) for _ in range(self.epoch_size)], []),
                          nn.Sequential(_Perturbation(self.pert_cb.p), self.model),
                          self.loss,
                          SGD,
                          self.lr,
                          train_bn=False,
                          default_cbs=False,
                          cbs=[_TrainLoop, Recorder(valid_metrics=False), ProgressCallback, BnFreeze,
                               self.pert_cb,
                               ReduceLROnPlateau('train_loss', min_delta=self.min_delta, min_lr=self.min_lr),
                               EarlyStoppingCallback('train_loss', min_delta=self.min_delta / 10)
                               ])
        learner.fit(self.n_epochs)
        return x.cpu() + self.pert_cb.p.data.detach().cpu()
