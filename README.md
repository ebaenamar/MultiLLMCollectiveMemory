# Multi-LLM Collective Memory Research Framework

## 🧠 Exploring the Emergence of Distributed Collective Memory in Multi-LLM Systems

This repository contains the experimental framework for investigating the impact of persistent collaborative memory between multiple LLM agents on complex multi-stage reasoning tasks.

### 📌 Main Hypothesis

Persistent collaborative memory between multiple LLM agents can significantly improve the efficiency and accuracy of complex multi-stage reasoning tasks under context constraints, compared to isolated memories or absence of memory.

### 🏗️ Project Structure

```
├── paper/                    # Research paper and documentation
├── experiments/             # Experimental configurations
├── agents/                  # Specialized agent implementations
├── memory_systems/          # Memory systems (shared, private, no memory)
├── benchmarks/             # Evaluation tasks and metrics
├── evaluation/             # Evaluation and analysis scripts
├── results/                # Experimental results and visualizations
└── docker/                 # Container configuration
```

### 🚀 Quick Start

1. **Set up environment:**
   ```bash
   docker-compose up -d
   ```

2. **Run basic experiment:**
   ```bash
   python experiments/run_benchmark.py --config configs/basic_comparison.yaml
   ```

3. **Analyze results:**
   ```bash
   python evaluation/analyze_results.py --experiment_id latest
   ```

### 📊 Experimental Configurations

- **Single Agent**: GPT-4 alone, no external memory (baseline)
- **Multi-Agent without memory**: Multiple LLMs with dialogue history only
- **Multi-Agent with shared memory**: Persistent common memory JSON/vector DB
- **Multi-Agent with private memory**: Each agent with isolated individual memory

### 🎯 Evaluation Metrics

- Final result accuracy
- Total number of tokens used
- Computational redundancy avoided
- Knowledge reuse rate
- Memory utilization (reads/writes)
- Incremental output quality

### 📝 Contributions

This work seeks to fill the gap in standard benchmarks that quantify the specific contribution of shared distributed memory in multi-LLM cognitive tasks.

---

**Author**: Eduardo Baena w Claude 4
**Institution**: Sundai Club
**Contact**: e.baena@northeastern.edu
