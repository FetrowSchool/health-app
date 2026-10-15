# **Assignment 3.1 — Research and Design**

## **Repository Information**

- **Repository URL:** https://github.com/FetrowSchool/health-app
- **Commit Hash:** 921b1f7a89e6497a3475fb7272b90a371ef5069b

## **Project Overview**

For Assignment 3, I designed a mental health app with the placeholder name "Pause". The app focuses on simplicity and accessibility. The application is currently planned to support two exercises: Paced Breathing and STOP. My goal is to make the app easy to navigate without unnecessary reading, typing, or complicated menus.

## **Application Design**

The application uses a mobile style interface with five main screens:

1. Daily mood check-in popup
2. Home screen with exercise selection
3. Paced Breathing exercise
4. STOP exercise
5. Completion and optional feedback

The daily mood check in asks users how they are feeling and allows them to select an option or skip. Users can then choose either exercise and each exercise is designed to take around 60 seconds. Users are able to exit exercises whenever they want. The interface uses large buttons, simple icons, and neutral colors to keep navigation straightforward.

## **Research-Based Decisions**

The design follows the research requirements R1–R4 and design principles D1–D6 provided in the assignment. These findings helped make decisions such as keeping exercises short, displaying one instruction at a time, minimizing required input, and allowing users to control their experience. Crisis support access remains visible throughout the application. The daily mood check in also provides a simple way to personalize the experience without requiring users to configure settings.


## **AI Integration and Data Storage**

The application will use a conversational language model to provide short, optional responses after exercises. The model will not control exercise steps, timing, navigation, or crisis-support access. 

The planned technology stack includes Vue, FastAPI, and SQLite. The database will store mood check-ins, exercise sessions, optional feedback, and conversation records. Saved activity may eventually help personalize the order of exercise options.

## **Safety and Accessibility**

The design includes a persistent crisis support button, skippable prompts, and the ability to leave exercises immediately and freely. The crisis support route will operate independently of the language model.

## **Design and Verification Evidence**


- [Application Design](docs/design.md)
- [Visual Mockups](docs/mockups/index.html)
- [User Flow Diagram](docs/user-flow.md)
- [Research Decisions](docs/research-decisions.md)
- [Verification Evidence](docs/verification.md)
- [README](README.md)
- [AGENTS.md](AGENTS.md)

The documentation links, research mappings, and required interface controls were checked. The five mockups were also reviewed visually in a browser.

## **Remaining Work**

Part 3.1 focused on design, so no working functionality was implemented. Part 3.2 will focus on building the exercises, connecting the language model, saving data, and implementing crisis-support access. Part 3.3 will focus on improving personalization, adding a way to review saved history, and completing the required fictional scenario testing and demonstrations.
