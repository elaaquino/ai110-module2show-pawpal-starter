# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions for user to perform: 
1. Enter basic owner + pet info
2. Add/edit tasks (duration + priority at minimum)
3. View today's tasks

- Briefly describe your initial UML design.

My initial UML design just contians the four classes I chose and the basic information/methods that need to be held within those classes.

- What classes did you include, and what responsibilities did you assign to each?

I included four classes, Owner, Pet, Task, and Scheduler. Owner and Pet contian the basic information needed to track an owner and a pet. The Task class tracks task type, constraints, priority, and duration. The Scheduler class tracks dates, raionale, generates a schedule, and explains why the plan was chosen.

**b. Design changes**

- Did your design change during implementation?

Yes.

- If yes, describe at least one change and why you made it.

Task didn't have a link back to its pet, so I added petID: str to Task. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The scheduler never assigns times to flexible tasks. It orders them but leaves them "flexible." Two tasks could both happen at 14:00 with no complaints, should one of those tasks be a flexible task.

- Why is that tradeoff reasonable for this scenario?

This tradeoff is reasonable because it lets the user complete their flexible tasks at a time it is best for them to do so, without being interrupted by other limitations in the scheduler.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
