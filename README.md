# miniUPS

**Author:** Meng Zhang, Yue Yu

**Description:**
An shipping system modeling UPS service to provide shipping service to simulated world and Amazon.
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
- User Friendly: Clear and intuitive user navigation bar, high feedback.
- High privacy and security: unauthorized users can only see simple package infomation,authorized users can query the whole package information and change delivery address.
- Scalability: utilized threadpool to handle high-frequency requests.

