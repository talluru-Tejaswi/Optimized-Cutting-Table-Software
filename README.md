# Optimized-Cutting-Table-Software
Optimized Cutting Table Software – a Django-based tool leveraging linear programming and genetic algorithms to minimize material waste and boost manufacturing efficiency with real-time visualization.
# 🧠 Layout Optimizer — GA + LP Hybrid (Material-Aware)

A smart cutting layout system for furniture manufacturing. Users can select templates (e.g. chair, table), material type (wood, plastic, metal), and tools (laser or blade), and the system auto-generates optimal layouts using Linear Programming (LP), Genetic Algorithm (GA), or Hybrid selection.

---

## ✅ Features

### 🪑 Furniture Templates
- Predefined templates for common furniture types
- Auto-generate pieces (width × height × quantity)

### 🔧 Tool Configurations
- Includes name, type (blade/laser), kerf, speed, power, focus
- Kerf dynamically affects layout efficiency

### 🪵 Material Handling
- `wood`, `plastic`, `metal`
- Material affects:
  - `extra_kerf`: added to base tool kerf
  - `min_spacing`: extra gap between parts

### ⚙️ Optimization Methods
- **LP (Linear Programming):**
  - Uses `rectpack` MaxRects
  - Dual-orientation support
- **GA (Genetic Algorithm):**
  - Rotation gene per piece
  - Crossover, mutation, elitism
- **Hybrid:**
  - Picks best result by:
    1. Most pieces placed
    2. Highest raw area
    3. Best utilization %

---

## 📊 Output Metrics

| Metric           | Description                              |
|------------------|------------------------------------------|
| `Utilization %`  | (Used area + kerf loss) / Stock area     |
| `Placed`         | Number of successfully placed pieces     |
| `Kerf Used`      | Final kerf after material adjustment     |
| `Layout Visual`  | Matplotlib rectangle plot                |

---

## 🧪 Testing Scenarios

### ✅ GA Wins:
```json
[
  { "width": 80, "height": 20, "quantity": 2 },
  { "width": 40, "height": 30, "quantity": 2 },
  { "width": 10, "height": 70, "quantity": 1 }
]
```
### ✅ LP Wins:

```json
[
  { "width": 30, "height": 30, "quantity": 4 },
  { "width": 20, "height": 20, "quantity": 4 },
  { "width": 10, "height": 10, "quantity": 8 }
]
```
## 📂 Notebook

- **File:** `O_C_T_S.ipynb`
- **Built in:** Google Colab
- **Description:** Full implementation including:
  - Setup & configuration
  - LP optimizer (MaxRects via rectpack)
  - GA optimizer (with rotation gene)
  - Hybrid selector logic
  - Visual layout plots
  - Utilization + kerf-aware metrics

---

## 🔜 Roadmap

- [ ] Export SVG/PDF for cutting machine
- [ ] Django integration (form: material + template + tool)
- [ ] User account save/load projects
- [ ] Multi-board layout support
- [ ] API endpoint for optimization-as-a-service

---

## 🧠 Tag
> “This project is the Layout Optimizer — uses GA, LP, Hybrid, with material-aware kerf logic. Notebook: `O_C_T_S.ipynb`. Continue from where we left off.”

---

## 💬 Session Log
- Optimization logic (GA, LP, Hybrid)
- Kerf-aware layout behavior
- Visual output + layout validation
- Smart result ranking (pieces → area → utilization)
