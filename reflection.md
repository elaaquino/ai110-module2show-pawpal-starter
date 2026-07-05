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

- I found that having the AI thoroughly explain any extra features/steps was helpful in implementing changes. Oftentimes, AI will try to improve things on its own without being told, and that can slip through the cracks. Having it specifically explain everything before fully adding changes helped a lot.

**b. What you would improve**

- Sometimes, I would ask the chatbot to list something to me, like the classes/features, but it would write it in the file I had open instead of just listing it in the chat. It caused a few problems for me, so in the future I'm gonna specify to list those types of things in the chat, or just close the file in the chat as a whole.

**c. Key takeaway**

- Using separpate chat sessions actually plays a big role in staying organized! It made it easy for me to refer to my original plans, testing, and general prompting based on suggestions or changes I needed to make. I'd honestly probably separate the chats even more based on file for future, larger projects.
