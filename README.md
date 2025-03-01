# lotSizing

# SINGLE LEVEL MULTI-ITEM LOT SIZING PROBLEM  
### WITH PERISHABLE ITEMS AND JOINT ORDERING UNDER CAPACITY CONSTRAINT AND LEAD TIMES

## 📌 Understanding the Problem  
This project focuses on the inventory management system of a chemical manufacturing company.  
The goal is to develop a more efficient ordering system that minimizes **holding and ordering costs** while ensuring timely availability of raw materials.

## ⚠️ Constraints and Key Considerations
- **Warehouse Capacity**: The raw material warehouse has a fixed storage limit.
- **Perishability**: Raw materials have a limited shelf life.
- **Lead Times**: Suppliers from different regions have varying delivery times.
- **Cost Factors**: The objective is to minimize:
  - Variable costs  
  - Item-specific fixed costs  
  - Joint fixed costs  
  - Inventory holding costs  
- **Supplier Selection**: Orders must be placed considering supplier constraints and pricing variations.

## 🔢 CPLEX Model  
A **mathematical model** was developed using **mixed-integer programming (MIP)** to determine the **optimal order quantity** and **supplier selection**.  
The model accounts for:
- Inventory constraints  
- Perishability  
- Lead times  
- Cost minimization  


## 🐍 Heuristic Approach (Python)
Since solving the problem for large datasets was **infeasible** with CPLEX, a **heuristic algorithm** was developed in **Python**.

**The algorithm:**
- Assigns suppliers to raw materials based on cost efficiency.
- Determines the latest possible order weeks to prevent shortages.
- Groups orders into joint batches to minimize fixed costs.
- Dynamically adjusts supplier selection based on cost reductions.


## 📊 Results and Implementation  
- The heuristic algorithm produced **near-optimal solutions**, with cost reductions in joint ordering and item-specific fixed costs.  
- Future improvements may focus on **refining batch merging strategies** and expanding the model for **real-time adjustments**.
