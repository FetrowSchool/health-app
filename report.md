# **Assignment 3.3 — finalization**

## **Repository Information**

- **Repository URL:** https://github.com/FetrowSchool/health-app
- **Commit Hash:** 7af8d903bd8d1112493e9d1e7946001671dcbd08

## **Project Overview**

For Assignment 3.3, I focused on finsihing and refining all the activies in Pause. The application supports PAced Breathing and 5-4-3-2-1 Sensory Grounding, along with an AI conversation feature that allows users to recive help from a model designed to be theraputic. 

The goal of this final part was to integrate the remaining feature, evaluate different scenrios, and verify that the app runs consitently. 


## **Application Features**

The application includes a daily mood check-in that appears once per day and allows users to select their mood. From the home screen, users can choose either exercise directly or use the AI-powered Help Me Choose feature.

Paced Breathing guides users through six cycles of 4 second inhales and 6 second exhales using an animated circle and countdown. Sensory Grounding guides users through the five senses using buttons to track their progress.

The application also includes an AI conversation interface which allows users to communicate with an AI assistant and receive suggestions based on how they are feeling or what they need. 

A history feature allows users to review their previous activity, while stored mood selections and exercise history support personalization.


## **AI Integration**

I integrated OpenRouter using the model nemotron 3 ultra.

The AI is used in two ways:

* Help Me Choose: Suggests an exercise based on the user’s selected focus, optional daily mood, and recent exercise history.
* Exercise Feedback: Generates short responses after users select Helpful or Not Helpful.

I also integrated a live ai voice model using GPT-Live-1.

This allows users to speak directly with the AI instead of relying only on the text-based options. The voice assistant is designed to be conversational and supportive while also offering practical suggestions and recommending exercises available in the application. The implementation uses WebRTC to handle live audio between the browser and OpenAI, while FastAPI manages session creation and keeps API credentials secure. Users can mute, end, or interrupt conversations, and the existing text-based features remain available.

## **Database and Persistence**

SQLite is used to save daily mood check-ins, exercise sessions, optional feedback, and supported conversation records.

The application uses saved information to personalize parts of the experience without automatically choosing exercises for users. The History feature provides a way to review previously completed exercises and available saved conversations.

## **Evaluation and Testing**

I evaluated Pause using at least fifteen fictional scenarios covering normal application use, exercise interactions, interruptions, and failure cases.

The evaluation also included three behavior checks focused on:

1. Crisis Support remaining accessible throughout the application.
2. Users maintaining control over exercises and navigation.
3. AI responses being unable to change the fixed exercise sequences.

Automated tests used mocked model responses to verify repeatable behavior. Selected fictional scenarios were also tested using live AI models to evaluate actual responses and variation.

Final verification results:

* Backend tests: 95 backend tests
* Frontend tests: 85 frontend tests
* Production build: Pass
* Fictional scenarios: 22/26 passed
* Behavior checks: 1/3 passed
* Clean-checkout verification: Pass

See the verification documentation for expected and observed results.

## **Demonstration**

Video link: https://drive.google.com/file/d/1JvCee75LmTHgC3xTfdIIPzEYWkHT8Dy0/view?usp=sharing


## **Design and Verification Evidence**


- [Application Design](docs/design.md)
- [Visual Mockups](docs/mockups/index.html)
- [User Flow Diagram](docs/user-flow.md)
- [Research Decisions](docs/research-decisions.md)
- [Verification Evidence](docs/verification.md)
- [README](README.md)
- [AGENTS.md](AGENTS.md)

The application was tested using automated tests, browser checks, and database inspection.

* 47 backend tests passed.
* 29 frontend tests passed.
* Production frontend build succeeded.
* Live OpenRouter recommendation and feedback requests succeeded.
* SQLite persistence was verified after restarting the backend.
* Paced Breathing completed in approximately 60 seconds.
* Grounding was designed for approximately 70 seconds at the intended pace.
* Mobile interface was checked at 390 × 844.

Mocked model responses were used for routine automated testing, while selected fictional scenarios were tested using the live model.


## **Changes from Part 3.1**
One major change was replacing the STOP exercise with 5-4-3-2-1 Sensory Grounding. After testing the exercise, I felt STOP was more like a reading exercise rather than a grounding, mental health exercise. This contradicts one of the core design philophies of having minmal reading. Sensory grounding provides more interaction while keeping a simple design. I also expanded the AI integration by adding Help Me Choose, giving the model a more meaningful role without removing user control. 

Paced breathing has also been changed to make it more interactive through a closed loop design.Instead of automatically starting when the exercise is opened, users now press and hold the breathing circle to begin. The exercise follows the same four-second inhale and six-second exhale pattern, but continues only while the button is held. Releasing the button pauses the exercise, and holding it again resumes from where the user stopped. This gives users more control over the exercise while allowing the application to detect their interaction. The intended exercise duration remains 60 seconds, but users can choose to continue longer or finish when they want.

## **Final Status and Findings**

Assignment 3.3 completes the devlopment and evalution for Pause. The app demonstrates the integration of Vue, FastAPI, SQLite, conversational AI, and live voice interaction within a mobile-style interface.

I'm happy with where this final version rest I did want to integrate the AI voice model into the 5-4-3-2-1 grounding, but I never quite got it to work. Besides that I did everything I set out to do and am satifed to leave this project here. 

One thing that surprised me about this project is just how sensitive the backend set up for voice integration is. When I was first trying to implement the voice integartion feature it would consitant fail to configure or would have connection issues and time out, even when the codex automatic tests would pass. I learned that relying on automatic tests isn't always a good idea and some things need to be tested indepently by a real user. 