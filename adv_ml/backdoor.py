# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/backdoor.ipynb.

# %% auto 0
__all__ = ['BackdoorAttack', 'DataPoisoningAttack', 'BadNetsAttack']

# %% ../nbs/backdoor.ipynb 3
from abc import ABC, abstractmethod
from typing import Dict


class BackdoorAttack(ABC):
    @abstractmethod
    def validate(self, learner) -> Dict:
        return {
            'ba': learner.validate()[1]
        }


# %% ../nbs/backdoor.ipynb 4
from dataclasses import dataclass

from fastai.vision.all import *


def _poisoned_dataset(clean, poison):
        all = clean + poison
        all.clean, all.poison = clean, poison
        if hasattr(clean, 'loss_func'):
            all.loss_func = clean.loss_func
        return all


@dataclass
class DataPoisoningAttack(BackdoorAttack):
    def __init__(self, poison_fraction=.1):
         super().__init__()
         store_attr('poison_fraction')

    def poison(self, dls: DataLoaders):
        self._poison_dl(dls.train)

    def _poison_dl(self, dl: DataLoader):
        poison_size = int(self.poison_fraction * len(dl.dataset))
        to_be_poisoned = self._subset_to_poison(dl.dataset, poison_size)
        dl.dataset = _poisoned_dataset(clean=dl.dataset - to_be_poisoned,
                                       poison=self._poison(to_be_poisoned))

    def _subset_to_poison(self, clean_train_dataset: Datasets, size: int) -> Datasets:
        return clean_train_dataset.random_sub_dsets(size)

    @abstractmethod
    def _poison(self, data_to_poison: Datasets):
        ...

# %% ../nbs/backdoor.ipynb 5
from typing import Dict
from fastai.vision.all import Datasets


class BadNetsAttack(DataPoisoningAttack):
    @delegates(DataPoisoningAttack)
    def __init__(self, trigger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger = trigger

    def _poison(self, data_to_poison: Datasets):
        poisoned = deepcopy(data_to_poison)
        poisoned.tls[0].tfms.add(mk_transform(self._insert_trigger))
        poisoned.tls[1].tfms = Pipeline([lambda _: '0', Categorize(['0'])])
        return poisoned

    def _insert_trigger(self, img):
        return type(img).create((np.array(img)+self.trigger) % 256)

    def validate(self, learner) -> Dict:
        asr_dl = self._poison(learner.dls.valid_ds).dl()
        learner.show_results(dl=asr_dl)
        return {**super().validate(learner), 'asr': learner.validate(dl=asr_dl)[1]}