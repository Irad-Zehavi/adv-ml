adv-ml
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Docs

See https://irad-zehavi.github.io/adv-ml/

## Install

``` sh
pip install adv_ml
```

## How to use

## How to Use

As an nbdev library, `adv-ml` supports `import *` (without importing
unwanted symbols):

``` python
from adv_ml.all import *
```

### Adversarial Examples

``` python
mnist = MNIST()
classifier = MLP(10)
learn = Learner(mnist.dls(), classifier, metrics=accuracy)
learn.fit(1)
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: left;">
      <th>epoch</th>
      <th>train_loss</th>
      <th>valid_loss</th>
      <th>accuracy</th>
      <th>time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>0.160490</td>
      <td>0.165644</td>
      <td>0.954900</td>
      <td>00:17</td>
    </tr>
  </tbody>
</table>

``` python
sub_dsets = mnist.valid.random_sub_dsets(64)
learn.show_results(shuffle=False, dl=sub_dsets.dl())
```

![](index_files/figure-commonmark/cell-4-output-2.png)

``` python
attack = InputOptimizer(classifier, LinfPGD(epsilon=.15), n_epochs=10)
perturbed_dsets = attack.perturb(sub_dsets)
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: left;">
      <th>epoch</th>
      <th>train_loss</th>
      <th>time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>-3.627444</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>1</td>
      <td>-6.452563</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>2</td>
      <td>-7.652328</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>3</td>
      <td>-8.258670</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>4</td>
      <td>-8.617092</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>5</td>
      <td>-8.851709</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>6</td>
      <td>-9.014016</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>7</td>
      <td>-9.130360</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>8</td>
      <td>-9.216579</td>
      <td>00:00</td>
    </tr>
    <tr>
      <td>9</td>
      <td>-9.281565</td>
      <td>00:00</td>
    </tr>
  </tbody>
</table>

``` python
learn.show_results(shuffle=False, dl=TfmdDL(perturbed_dsets))
```

![](index_files/figure-commonmark/cell-6-output-2.png)
