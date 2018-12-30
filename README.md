# LoopMC

This repo contains all the relevant sourced related to our ACSAC 2018 paper: [`LoopMC: Using Loops For Malware Classification Resilient to
Feature-unaware Perturbations`](https://dl.acm.org/citation.cfm?id=3274731).

## Utils
The folder `utils` contains individual utils related to our work.

### Semantic labeling
We provided a standalone version of our semantic labeling technique, which will give a semantic label from `method name`, `class` and, `method signature`.

How to use it:
```
cd utils
# ipython
In [1]: import semantic_labeling as sl

In [2]: sl.get_method_label_by_name('equals', 'Ljava/lang/Object;', 'equals(Ljava/lang/Object;)Z')

Out[2]: 'ObjectComparision'
```
You can import the `semantic_labeling` module into your projects and use it as illustrated above.
