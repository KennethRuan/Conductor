# Conductor

## Inspiration
In this pandemic-ridden world, regular day-to-day actions such as touching a surface become exponentially more dangerous. Appliances such as public computers and other types of technology become much harder to use without risking your health. With Conductor™, this problem is solved in a unique and elegant manner, using nothing but your hands and a webcam!

## What it does
Our program allows users to control their mouse completely free of any physical contact. It detects specific hand gestures and movements from a webcam and translates them to mouse movements, allowing them to use devices as if they had a real mouse.

## How We built it
Using a webcam, image manipulation, and a lot of math, we were able to find and isolate the locations of each finger on the hand. The positions of the fingers, both on the screen and relative to each other, can be used to determine how much the mouse moves on the screen and what action (such as clicking) to perform.

Our program uses novel strategies such as background subtraction in order to ensure an accurate yet fast prediction. The objective of Conductor is to be as accessible as possible, so the program was benchmarked on standard CPUs such as the AMD Ryzen 5 and Intel i5. Utilizing pattern recognition and image manipulation to locate the palm and to segment the wrist and fingers we are able to produce an accurate prediction in 0.02s.

## Challenges We ran into
The main challenge that we ran into while creating our program was developing an algorithm to accurately interpret the data we had at hand. Due to our program being runnable using nothing but a webcam, we had to solve various issues such as dealing with image transformations and correctly identifying the palm of the hand, correctly segmenting the fingers into their own separate parts, identifying which fingers are being held up, and many more. We were able to solve these challenges by brainstorming more about the challenge at hand and recognizing the different types of data that may “break” our program, then modifying our algorithm to detect these types of data and correct them using various helper programs, such that they can be correctly analyzed by the rest of our program.

## Accomplishments that we're proud of
With the difficulty of our project comes many things we’re proud of accomplishing. Successfully detecting hand and finger position, as frustrating as it may be, is something we can proudly say we achieved. We also developed a method to reduce cursor jitter.

## How our program works
Because of how math and image processing-intensive our program was, one of the biggest things that we learned throughout developing this program is the specific math and algorithms required for interpreting our data and converting it into recognizable gestures that can be used for mouse input. For example, we used convex hulls, bounding boxes, and various image transformations to isolate the user’s hand into an upright, black-and-white image, ensuring that the arm gets taken out of the image. We then used an algorithm to identify and remove the palm and thumb, isolating the fingers such that they can be recognized as their own connected component, in order to identify the location of the fingers and which specific finger is being held up at any given time.

## What's next for Conductor
In the timespan of 36 hours, we weren’t able to completely perfect our program - there are a lot of opportunities for us to improve our program in the future! We plan on adding more customizable and more hand gestures for actions such as scrolling, double-clicking, or customizable gestures within our program that can map to certain hotkeys or commands. We also plan on further optimizing the speed and accuracy program to make it run as smoothly as possible.
