# Project Description:

In your city, there’s a library where you can borrow books and pay for your borrowings using cash, depending on how many days it takes you to read the book. The problem is that the library’s system of
tracking books, borrowings, users, and payments is outdated – everything is done manually and all tracking is performed on paper. There’s no possibility to check the inventory of specific books in the
library. Also, you have to pay with cash (no credit card support). The library administration never knows who returned their book in time and who didn’t.

In this project, you’ll be fixing all these problems. To do so, you’ll implement an online management system for book borrowings. The system will optimize the library administrators’ work and make the
service much more user-friendly.

The task doesn’t currently require a front-end. The website should be fully functional through a browsable API interface.

## **Requirements**:

1. Functional (what the system should do):

   - a. Web-based
   - b. Manage books inventory
   - c. Manage books borrowing
   - d. Manage customers
   - e. Display notifications
   - f. Handle payments

2. Non-functional (what the system should deal with):

   - a. 5 concurrent users
   - b. Up to 1000 books
   - c. 50k borrowings/year
   - d. ~30MB/year

## **Architecture**:

**DB schema** ![DB schema](images/structure.png)

## **Resources**:

1. Book:

   - a. Title: str
   - b. Author: str
   - c. Cover: Enum: HARD | SOFT
   - d. Inventory\*: positive int
   - e. Daily fee: decimal (in $USD)

   \* Inventory – the number of this specific book available now in the library

2. User (Customer):

   - a. Email: str
   - b. First name: str
   - c. Last name: str
   - d. Password: str
   - f. Is staff: bool

3. Borrowing:

   - a. Borrow date: date
   - b. Expected return date: date
   - c. Actual return date: date
   - d. Book id: int
   - f. User id: int

4. Payment: Status: Enum: PENDING | PAID

   - a. Type: Enum: PAYMENT | FINE
   - b. Borrowing id: int
   - c. Session url: Url # url to stripe payment session
   - d. Session id: str # id of stripe payment session
   - f. Money to pay: decimal (in $USD) # calculated borrowing total price

## **Components**:

1. Books Service:

   - a. Managing the quantity of books (CRUD for Books)
   - b. API:
        <ol type="I">
            <li>POST: books/            - add new</li>
            <li>GET: books/             - get a list of books</li>
            <li>GET: books/<id>/        - get book detail info</li>
            <li>PUT/PATCH: books/<id>/  - update book (also manage inventory)<li>
            <li>DELETE: books/<id>/     - delete book</li>
        </ol>

2. Users Service:

   - a. Managing authentication & user registration
   - b. API:
        <ol type="I">
            </li>POST: users/                   - register a new user<li>
            </li>POST: users/token/             - get JWT tokens<li>
            </li>POST: users/token/refresh/     - refresh JWT token<li>
            </li>GET: users/me/                 - get my profile info<li>
            </li>PUT/PATCH: users/me/           - update profile info<li>
        </ol>

3. Borrowings Service:

   - a. Managing users' borrowings of books
   - b. API:
       <ol type="I">
           <li>POST: borrowings/    - add new borrowing (when borrow book - inventory should be made -= 1)</li>
           <li>GET: borrowings/?user_id=...&is_active=...   - get borrowings by user id and whether is borrowing still active or not.</li>
           <li>GET: borrowings/<id>/    - get specific borrowing</li>
           <li>POST: borrowings/<id>/return/    - set actual return date (inventory should be made += 1)</li>
       </ol>

4. Notifications Service (Telegram):

   - a. Notifications about new borrowing created, borrowings overdue & successful
   - b. In parallel cluster/process (Django Q package or Django Celery will be used)
   - c. Other services interact with it to send notifications to library administrators.
   - d. Usage of Telegram API, Telegram Chats & Bots.

5. Payments Service (Stripe):

   - a. Perform payments for book borrowings through the platform.
   - b. Interact with Stripe API using the `stripe` package.
   - c. API:
        <ol type="I">
            <li> GET: success/  - check successful stripe payment</li>
            <li>GET: cancel/    - return payment paused message</li>
        <ol>

6. View Service (Delegated to the Front-end Team):

   - a. Front-end interface for communication with Library API.
   - b. Will not be implemented here
