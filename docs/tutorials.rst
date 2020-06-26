*********
Tutorials
*********

Clustering
==========
The following tutorials demonstrate the effectiveness of clustering algorithms designed specifically
for multiview datasets.

.. toctree::
   :maxdepth: 1
   
   tutorials/cluster/MVKMeans/MultiviewKMeans_Tutorial
   tutorials/cluster/MVKMeans/MultiviewKmeansValidation_ComplexData
   tutorials/cluster/MVKMeans/MultiviewKmeansValidation_SimulatedData
   tutorials/cluster/MVSpectralClustering/MultiviewSpectralClustering_Tutorial
   tutorials/cluster/MVSpectralClustering/MultiviewSpectralValidation_ComplexData
   tutorials/cluster/MVSpectralClustering/MultiviewSpectralValidation_SimulatedData
   tutorials/cluster/MVSphericalKMeans/MVSphericalKMeans_Tutorial
   tutorials/cluster/MVSphericalKMeans/MVSphericalValidation_SimulatedData
   tutorials/cluster/MVCoregSpectral/MVCoregularizedSpectral_Tutorial
   tutorials/cluster/multiview_vs_singleview_clustering

Semi-Supervised
===============
The following tutorials demonstrate how effectiveness of cotraining in certain multiview scenarios to 
boost accuracy over single view methods.

.. toctree::
   :maxdepth: 1
   
   tutorials/semi_supervised/cotraining_classification_exampleusage
   tutorials/semi_supervised/cotraining_classification_simulatedperformance
   tutorials/semi_supervised/cotraining_regression_exampleusage

Embedding
=========
Inference on and visualization of multiview data often requires low-dimensional representations of the data, known as *embeddings*. Below are tutorials for computing such embeddings on multiview data.

.. toctree::
   :maxdepth: 1
   
   tutorials/embed/gcca_tutorial
   tutorials/embed/gcca_simulation
   tutorials/embed/kcca_tutorial
   tutorials/embed/kcca_icd_tutorial
   tutorials/embed/dcca_tutorial
   tutorials/embed/cca_comparison
   tutorials/embed/mvmds_tutorial
   tutorials/embed/mvmds_proof
   tutorials/embed/Omnibus Embedding for Multiview Data
   tutorials/embed/SplitAE Tutorial
   tutorials/embed/SplitAE Simulated Data

Factorization
=============
The following tutorials show how to use multi-view factorization algorithms.

.. toctree::
   :maxdepth: 1

   tutorials/factorization/ajive_tutorial

Plotting
========
Methods build on top of Matplotlib and Seaborn have been implemented for convenient plotting of multiview data. See examples of such plots on simulated data.

.. toctree::
   :maxdepth: 1

   tutorials/plotting/quick_visualize_tutorial
   tutorials/plotting/crossviews_plot
   
Test Dataset
============
In order to conviently run tools in this package on multview data, data can be simulated or  be accessed from the publicly available `UCI multiple features dataset <https://archive.ics.uci.edu/ml/datasets/Multiple+Features>`_ using a dataloader in this package.

.. toctree::
   :maxdepth: 1

   tutorials/datasets/load_UCImultifeature
   tutorials/datasets/GaussianMixtures
   tutorials/cluster/multiview_vs_singleview_clustering
