# **Assignment 3.1 — Research and Design**

## **Repository Information**

- **Repository URL:** [Insert GitHub Repository URL]
- **Commit Hash:** [Insert Commit Hash]

## **Project Overview**

For Assignment 3, I designed Pause, a mental health skills application focused on simplicity and accessibility. The application supports two exercises: Paced Breathing and STOP. The goal is to make it easy for users to navigate exercises without unnecessary reading, typing, or complicated menus.

## **Application Design**

The application uses a mobile-style interface with five main screens:

1. Daily mood check-in popup
2. Home screen with exercise selection
3. Paced Breathing exercise
4. STOP exercise
5. Completion and optional feedback

The daily mood check-in asks users how they are feeling and allows them to select an option or skip. Users can then choose either exercise. Each exercise is designed to take approximately 60 seconds, and users can exit whenever they want.

The interface uses large buttons, simple icons, and neutral colors to keep navigation straightforward.

## **Research-Based Decisions**

The design follows the research requirements R1–R4 and design principles D1–D6 provided in the assignment.

These findings influenced decisions such as keeping exercises short, displaying one instruction at a time, minimizing required input, and allowing users to control their experience. Crisis-support access remains visible throughout the application.

The daily mood check-in also provides a simple way to personalize the experience without requiring users to configure settings.

See Research Decisions for the complete research mapping.

## **AI Integration and Data Storage**

The application will use a conversational language model to provide short, optional responses after exercises. The model will not control exercise steps, timing, navigation, or crisis-support access.

The planned technology stack includes Vue, FastAPI, and SQLite. The database will store mood check-ins, exercise sessions, optional feedback, and conversation records. Saved activity may eventually help personalize the order of exercise options.

## **Safety and Accessibility**

Pause is a coursework prototype and is not intended to provide therapy or clinical support. Testing will use fictional scenarios only.

The design includes a persistent crisis-support button, skippable prompts, and the ability to leave exercises immediately. The crisis-support route will operate independently of the language model.

## **Design and Verification Evidence**

- Application Design
- User Flow Diagram
- Research Decisions
- Verification Notes
- Visual Mockups

The documentation links, research mappings, and required interface controls were checked. The five mockups were also reviewed visually in a browser at a mobile viewport.

## **Remaining Work**

Part 3.1 focused on design, so no working application functionality was implemented. Part 3.2 will focus on building the exercises, connecting the language model, saving data, and implementing crisis-support access.

Part 3.3 will focus on improving personalization, adding a way to review saved history, and completing the required fictional scenario testing and demonstrations.
