# miniUPS

**Author:** Meng Zhang, Yue Yu

**Description:**
A shipping system modeling UPS service to provide shipping service to simulated worlds and the Amazon.
The service is developed with **Django** and used **Google Protocol** to communicate among UPS, World and Amazon. 

---
**Relation of UPS & Amazon**

<img width="543" alt="image" src="https://user-images.githubusercontent.com/60654350/180844842-6cf3a4fd-7ba6-4648-bb43-284d33dd4aa9.png">

---
**Run**
```
python3 manage.py runserver
```
This will automatically run the frontend web service. 


```
python3 server.py
```
This will automatically run the backend service.

---
**Preview**

https://github.com/yuy-e/miniUPS/blob/main/differentiation.pdf

---
**Features**
- Supports Multi-Worlds throught individual world-id.
- User Friendly: Clear and intuitive user navigation bar, high feedback. When a pacakge is delivered, we will send the owner emails to notify them the pacakge is delivered to inform them to pick up in time. 
- High privacy and security: We protect our system from registration injection attack. For unauthorized users, they can only see simple package infomation. For authorized users, they can query the whole package information and change delivery address.
- Scalability: utilized threadpool to handle high-frequency requests.

