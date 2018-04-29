The Choracle
=======

This was my final project for my Sensors & Transducers class at UGA.  It's a simple python script that takes a .WAV file of a chord as an input and outputs the notes that are in the chord.  The horrible title is a portmanteau of "chord" and "oracle".  

It works by performing a Fourier transform and then computing the "Harmonic Product Spectrum", i.e. taking the geometric means of the magnitudes of the Fourier spectrum for a base note and a set of its low harmonics - right now, we consider 5 harmonics (this seems to be about the sweet spot) across the standard pitches from E2 to E4 (this is just a demonstration, and should be expanded to include the full range of notes that one would expect to be present in a chord).  The program simply outputs the notes corresponding to the 5 greatest harmonic products. 

The Harmonic Product Spectrum is cool - it's a simple concept (with surprisingly little academic research) that extends the Fourier transform's frequency domain representation, where instead of representing the strength of an individual frequency or a single sine wave, we have a quantity that represents the presence of a true musical note - *including its harmonics, and invariant of its timbre*.

Included is `gmaj.wav`, a G Major I recorded on my guitar.  For example, run:

`python run.py gmaj.wav`