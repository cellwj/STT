# 部署

- ❌ Windows
- ✅ Ubuntu
```bash
sudo apt update && sudo apt upgrade
sudo apt install petsc-dev
conda create -n stt python==3.7.6
conda activate stt
pip install -r requirements.txt
```

# 复现

## `./example_notebooks/`

| 文件名                            | 跑通 | 备注                     |
|----------------------------------|--------------|------------------------|
| example_emt_circuit.ipynb        |       ✅       |                           |
| example_toggle.ipynb             |     ❌         |  FileNotFoundError: `data/results_celldancer.h5ad`  `data/results_unit.h5ad`                       |
| example-bone_marrow.ipynb        |      ✅        |    |
| example-bone-marrow.ipynb        |    ❌       | 内存不足 |
| example-chicken_heart.ipynb      |      ❌        | FileNotFoundError `data/ch_results.h5ad`           |
| example-drosophila.ipynb         |      ❌        |   FileNotFoundError `data/E8-10_b_S21.h5ad`                 |
| example-emt.ipynb                |      ❌        |   内存不足  |
| example-mouse_brain_bin.ipynb    |      ❌        | 内存不足  |
| example-mouse_brain-spatial.ipynb|       ✅        |   |
| example-mouse_eryth.ipynb        |     ✅          |    |
| example-pancreas.ipynb           |     ✅         |    |
| toggle_benchmark.ipynb           |     ✅         |    |

*注1：代码调用 `st.tl.compute_pathway` 和 `st.dynamical_iteration` 时会出现“PETSC ERROR”，不会影响代码执行，忽略即可。*

*注2：每个文件的运行时长均在四十分钟左右。*

## `./example_notebooks/comparison/`

| 文件名                          | 跑通 | 备注           |
|---------------------------------|------|----------------|
| celldancer-emt-a549.ipynb       | ❌   | FileNotFoundError `../../data/A549_TGFB1.h5ad` |
| celldancer-emt.ipynb            | ✅   |             |
| celldancer-mouse-brain.ipynb    | ✅   |             |
| celldancer-toggle.ipynb         | ✅   |             |
| dynamo-emt.ipynb                | ✅   |             |
| dynamo-toggle.ipynb             | ✅   |             |
| unitevelo-a549.ipynb            |    |             |
| unitevelo-emt.ipynb             |    |             |
| unitevelo-mouse-brain.ipynb     |    |             |
| unitevelo-toggle.ipynb          |    |             |

---
# STT

## Introduction
We present a spatial transition tensor (STT) method that utilizes mRNA splicing and spatial transcriptomes through a multiscale dynamical model to characterize multi-stability in space. By learning a four-dimensional transition tensor and spatial-constrained random walk, STT reconstructs cell-state specific dynamics and spatial state-transitions via both short-time local tensor streamlines between cells and long-time transition paths among attractors. Overall, STT provides a consistent multiscale description of single-cell transcriptome data across multiple spatiotemporal scales. 


<img src="https://github.com/cliffzhou92/STT/blob/main/img/Picture1.png" width="800">

## Get Started
Install the dependencies by ``pip install -r requirements.txt``, and change directory to the ``./example_notebooks``. Run the results with Jupyter Lab.

In MAC OS, if there's an issue with installing ptsc-related packages, it's recommended to refer to the trouble shooting [here](https://pygpcca.readthedocs.io/en/latest/installation.html). Or below is alternative way to install in a seprate conda environment:

```bash
conda create -n stt python==3.7.6
conda activate stt
brew install gcc open-mpi openblas lapack arpack
conda install -c conda-forge pygpcca
pip install -r requirements-macos.txt
```

## Basic Usage and Tutorials
```python
import sctt as st
adata.obs['attractor'] =  # initialize the attractor, can use leiden or original annotation
adata_aggr = st.dynamical_iteration(adata,n_states =K, n_iter = 20, weight_connectivities = 0.5, n_neighbors = 100, n_components = 20,thresh_ms_gene = 0,thresh_entropy = 0.1)
# n_states: number of attractors
# n_iter: maximum of iteration
# thresh_entropy: the threshold of entropy difference between iterations to halt iteration, default is 0.1
# weight_connectivities: the weight of diffusion kernel as opposed to velocity kernel, default is 0.5
# n_neighbors: number of neighbors used to construct cellular random walk, default is 100
# n_component: number of eigen components to use in GPCCA decomposition, default is 20
# thresh_ms_gene: the threshold of minimum multi-stability score of genes to include when constructing random walk, default is 0
st.infer_lineage(adata,si=4,sf=3) # infer and plot the transition path
st.plot_tensor(adata, adata_aggr,  basis = 'trans_coord',list_attractor = [0,1,2,3]) # plot the transition tensor components
st.plot_top_genes(adata, top_genes = 10) # plot the U-S diagram of top genes with the highest multi-stability score

```
The documentations of function APIs are available at [here](https://stt-doc.readthedocs.io/en/latest/) and the website is under active development to include more tutorials.

The available tutorials are also provided as annotated Jupyter notebooks below.

[Tutorial 1:Basic Usage and Application on Toggle-switch Simulation Dataset](https://github.com/cliffzhou92/STT/blob/release/example_notebooks/example_toggle.ipynb)

[Tutorial 2:Analysis of Spatial Data,Pathway Visualization and Parameter sensitivity](https://github.com/cliffzhou92/STT/blob/release/example_notebooks/example-mouse_brain-spatial.ipynb)

[Tutorial 3:Analysis of Chicken Heart Spatial Data, Dynamical Manifold and Transition Path Inference](https://github.com/cliffzhou92/STT/blob/release/example_notebooks/example-chicken_heart.ipynb)


## Example Notebooks
**System** | **Data Source** | **Notebook File**
------------| -------------- | ------------
EMT circuit | [Simulation Data](https://github.com/cliffzhou92/STT/tree/main/data/emt_sim/Generating_Dataset.ipynb) in this study |[notebook](https://github.com/cliffzhou92/scTT/blob/main/example_notebooks/example_emt_circuit.ipynb)
EMT of A549 cell lines |[Cook et al.](https://www.nature.com/articles/s41467-020-16066-2)|[notebook](https://github.com/cliffzhou92/STT/blob/main/example_notebooks/example-emt.ipynb)
Erythroid lineage in mouse gastrulation |[Pijuan-Sala et al.](https://www.nature.com/articles/s41586-019-0933-9) and [scVelo](https://scvelo.readthedocs.io/scvelo.datasets.gastrulation_erythroid/)|[notebook](https://github.com/cliffzhou92/STT/blob/main/example_notebooks/example-mouse_eryth.ipynb)
Adult human bone marrow | [Setty et al.](https://www.nature.com/articles/s41587-019-0068-4) and [scVelo](https://scvelo.readthedocs.io/scvelo.datasets.bonemarrow/)| [notebook](https://github.com/cliffzhou92/STT/blob/main/example_notebooks/example-bone_marrow.ipynb)
Developing Chicken Heart | [Mantri et al.](https://www.nature.com/articles/s41467-021-21892-z) and [SIRV](https://zenodo.org/record/6798659)| [notebook](https://github.com/cliffzhou92/STT/blob/main/example_notebooks/example-chicken_heart.ipynb)

