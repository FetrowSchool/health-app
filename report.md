# **Assignment 3.1 — Research and Design**

## **Repository Information**

- **Repository URL:** https://github.com/FetrowSchool/health-app
- **Commit Hash:** 9df81008087e029a38dd1d68b661fbbfc4d75b67

## **Project Overview**

For Assignment 3.2, I developed a working version of "Pause", a mental health skills application designed around simplicity and accessibility. The application now has two working exercises: Paced Breathing and 5-4-3-2-1 Sensory Grounding.

The goal was to create an app that allows users to complete exercises with minimal reading, typing, or unnecessary navigation.

## **Application Features**

The application includes a daily mood check-in that appears once per day and allows users to select their mood. From the home screen, users can choose either exercise directly or use the AI-powered Help Me Choose feature.

Paced Breathing guides users through six cycles of 4 second inhales and 6 second exhales using an animated circle and countdown. Sensory Grounding guides users through the five senses using buttons to track their progress. All exercises and screens allow users to exit at any time and Crisis Support remains accessible the whole time.

## **Research-Based Decisions**

The design follows the research requirements R1–R4 and design principles D1–D6 provided in the assignment. These findings helped make decisions such as keeping exercises short, displaying one instruction at a time, minimizing required input, and allowing users to control their experience. Crisis support access remains visible throughout the application. The daily mood check in also provides a simple way to personalize the experience without requiring users to configure settings.


## **AI Integration**

I integrated OpenRouter using the model nemotron 3 ultra.

The AI is used in two ways:

* Help Me Choose: Suggests an exercise based on the user’s selected focus, optional daily mood, and recent exercise history.
* Exercise Feedback: Generates short responses after users select Helpful or Not Helpful.

I also integrated a live ai voice model using GPT-Live-1.

This allows users to speak directly with the AI instead of relying only on the text-based options. The voice assistant is designed to be conversational and supportive while also offering practical suggestions and recommending exercises available in the application. The implementation uses WebRTC to handle live audio between the browser and OpenAI, while FastAPI manages session creation and keeps API credentials secure. Users can mute, end, or interrupt conversations, and the existing text-based features remain available.

## **Database and Persistence**

The application uses SQLite to save daily check ins, exercise sessions, optional feedback, and AI conversations.  

Database persistence was verified by restarting the backend and confirming that saved records remained available.

## **Safety and Accessibility**

Crisis Support is available independently of the language model and backend. Users can exit exercises immediately, skip optional prompts, and return home during AI requests or failures.

The interface uses large labeled buttons, simple navigation, neutral colors, and reduced-motion support.

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

## **Remaining Work**

Part 3.3 will focus on further refinement, reviewing saved history, and completing the required evaluation using at least fifteen fictional scenarios and three behavior checks.

Current limitations include the possibility of interrupted sessions remaining marked as started and incomplete screen-reader and zoom accessibility testing.
