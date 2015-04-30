.. EMG-Visualization-Project documentation. Taxonomy file.
   Defines words used in the context of EMG experiments and servers the
   purpose of disambiguation

********
Taxonomy
********
This chapter introduces expressions used in the context of this project. This
is how it is used in the BRML lab. Other institutions and literature might use
different expressions for the same thing, also they most likely mean something
entirely different in other areas.

===========
Hypothesis
===========
A (scientific) problem which is to be validated experimentally. It could also be
said a hypothesis is a question for which an answer is sought.

======
Setup
======
Overhead needed to set up an experiment. This includes the configuration of the
hardware and software, how to record data, how the experiment is to be conducted
and so on.

==========
Experiment
==========
A process resulting in the acceptance or rejection of the hypothesis (answer to
the question asked).

The term experiment as used in this context can be compared to a study in
medicine. It is a process possibly spanning over a longer period of time.
However, there is not just one experiment, but different experiments are
conducted to come to a conclusion.

========
Modality
========
Can be summarized as a group of sensors. Using an EMG, all the electrodes are a
modality (resulting in the EMG signal) depending on the setup subsets of sensors
might form a modality (e.g. if interested in different muscles).

Another example is a tracking system. Here not the cameras are the modality, but
the positions extracted from them.

=======
Data
=======
Consists of everything used to determine whether or not to accept/reject the
hypothesis.

=======
Subject
========
A clearly differentiably entity (person).

========
Session
========
A session is the conduction of an experiment with a certain setup and one
subject over a certain amount of time. Note, that a session might result in
multiple recordings.

Changing the subject, the experiment or the setup does result in a new session.
Changing the time (conducting an experiment with the same person and the same
setup again) does not always result in a new session. If the time span between
the conductions is small (for example drink a glass of water, go to the toilet,
etc) or the conductions are even consecutive, then it is still one session. If
hours, days or even weeks are between two conductions then it is a new session.
This is not well defined and might differ for different occassions.

========
Recording
=======
A stream of continuous data produced during one session. A recording may contain
multiple trials.

========
Trial
========
The smallest amount of data needed to decide, whether or not to accept or reject
the hypothesis.

For example, to determine if it is possible to identify how a limb moves through
space it would theoretically suffice to record one movement of one person. 

======
Sample
======
Smallest measurable fraction of one modality. In case of an EMG this would be
one electrode.
    
