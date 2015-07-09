.. EMG-Visualization-Project documentation Introduction file
   Contains the introductory chapter introducing EMG and explaining a
   little bit what ML is about

************
Introduction
************
The EMG-Visualization-Project is a joined project between the TU Munich faculty
of informatics and faculty of sports and initialized in the scope of an
Interdisciplinary Project (IDP).

The goal of the EMG-Visualization-Project is to give a framework for
Electromyography (EMG) Data visualization. This framework is not intendet for
experts in that you have to now python. The goal of this project is not to
provide an easy to use graphical interface.

The EMG-Visualization-Project utilizes IPython Notebook through which
functionality provided by custom scripts is made available.
This makes it possible to easily set up a workflow to preprocess EMG data.

The following sections will introduce EMG and also some concepts of Machine
Learning.

================
Electromyography
================
An EMG measures electrical current generated in muscles during its contraction.
These measures represent neurmuscular activities.

As to how this electrical signal comes into existence. As a whole the human
body is electically neutral. On the cellular level exist a potential difference
between intra-cellular and extra-cellular fluids, though. If a person decides
to contract a muscle, a stimulus from a neuron is send. This stimulus causes the
cells in the muscle fibre to depolarize as the stimulus propagates along its
surface (i.e. the muscles twitches). This depolarization is accompanied by a
movement of ions which induces an electrical field near each muscle fibre,
which is measured with the EMG electrodes.

The induced field can be measured by electrodes being placed on the skin of a
person (sEMG) or by electrodes being placed in the muscle. The advantages and
disadvantages of these approaches are obvious. The sEMG is easy to administer
but the measured signals are unprecise and noisy, whereas the intramuscular
provides better measurements but is difficult to administer.

The measured signal usually has (before amplification) an amplitude of 0-10mV
and ranges between :math:`\pm5mV`.

A EMG measurement always consists of multiple Motor Unit Activation Potentials
(MUAPs), that is electrical fields of different muscles. Luckily, MUAPs from
different muscles have different characteristics and therefore a signal can be
decomposed into its constituting MUAPs using mathematical tools like `wavelet
transform <http://en.wikipedia.org/wiki/Wavelet_transform>`_ or `fourier
transform <http://en.wikipedia.org/wiki/Fourier_transform>`_.

================
Machine Learning
================
TODO: Should put emphasis on how ML is used in the context of this project.

