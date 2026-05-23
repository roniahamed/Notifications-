# **Backend Developer Task (Python/Django Focused)**

## **Task: Background Job Based Notification System**

Build a backend API where users can schedule notifications.

### **Requirements**

Use:

* Django \+ Django REST Framework  
* Celery/Redis integration  
* PostgreSQL  
* Docker
* SMTP
* Web Socket
* Firebase Cloud Messaging

### **Features**

Create APIs for:

* User authentication  - register, login, logout, refresh token, verify otp by email, forgot password, reset password using django rest framework simple jwt and send email for verification, forgot password, reset password using django smtp
* Create notification (with title, message, scheduled time) by user (after login), notification will be sent at the scheduled time from celery worker using django smtp - also send in app notification by web socket and firebase cloud messaging
* Schedule notification (using celery)
* View my notification history (with pagination, searching, filtering, sorting)  by user (after login)
* Retry failed notification (with retry logic) by user (after login) 

### **Notification Object**

Each notification contains:

* Title  
* Message  
* Scheduled Time  
* Status  
* Retry Count

### **Critical Thinking Requirements**

Candidate must handle:

* Time validation  
* Failed job handling  
* Retry logic  
* Background processing  
* API security  
* Edge cases  
* Queue/job architecture thinking

### **Extra Problem-Solving Condition**

If scheduled time is in the past:

* API should reject the request

If notification fails 3 times:

* Mark as permanently failed  
* Prevent infinite retries

### **Bonus**

* Celery/Redis integration  
* Docker Compose setup  
* Logging & monitoring

### **Evaluation Focus**

* Backend architecture  
* Queue logic understanding  
* Security  
* Scalability thinking  
* Database design  
* Clean API structure  
* Error handling quality



# don't be write extra and unnessery commment and documnet in code just do the task and write the nessesry comment. 

