# Multi-LLM Collective Memory Research Framework

## 🧠 Exploración de la Emergencia de Memoria Colectiva Distribuida en Sistemas Multi-LLM

Este repositorio contiene el framework experimental para investigar el impacto de la memoria colaborativa persistente entre múltiples agentes LLM en tareas complejas de razonamiento multietapa.

### 📌 Hipótesis Principal

La memoria colaborativa persistente entre múltiples agentes LLM puede mejorar significativamente la eficiencia y precisión de tareas complejas de razonamiento multietapa bajo restricciones de contexto, en comparación con memorias aisladas o ausencia de memoria.

### 🏗️ Estructura del Proyecto

```
├── paper/                    # Paper de investigación y documentación
├── experiments/             # Configuraciones experimentales
├── agents/                  # Implementación de agentes especializados
├── memory_systems/          # Sistemas de memoria (compartida, privada, sin memoria)
├── benchmarks/             # Tareas de evaluación y métricas
├── evaluation/             # Scripts de evaluación y análisis
├── results/                # Resultados experimentales y visualizaciones
└── docker/                 # Configuración de contenedores
```

### 🚀 Inicio Rápido

1. **Configurar entorno:**
   ```bash
   docker-compose up -d
   ```

2. **Ejecutar experimento básico:**
   ```bash
   python experiments/run_benchmark.py --config configs/basic_comparison.yaml
   ```

3. **Analizar resultados:**
   ```bash
   python evaluation/analyze_results.py --experiment_id latest
   ```

### 📊 Configuraciones Experimentales

- **Single Agent**: GPT-4 solo, sin memoria externa (baseline)
- **Multi-Agente sin memoria**: Múltiples LLMs con solo historial de diálogo
- **Multi-Agente con memoria compartida**: Memoria común persistente JSON/vector DB
- **Multi-Agente con memoria privada**: Cada agente con memoria individual aislada

### 🎯 Métricas de Evaluación

- Accuracy del resultado final
- Número de tokens totales utilizados
- Redundancia computacional evitada
- Tasa de reutilización de conocimientos
- Utilización de memoria (lecturas/escrituras)
- Calidad incremental del output

### 📝 Contribuciones

Este trabajo busca llenar el vacío en benchmarks estándar que cuantifiquen la contribución específica de la memoria distribuida compartida en tareas cognitivas multi-LLM.

---

**Autor**: [Tu nombre]  
**Institución**: [Tu institución]  
**Contacto**: [Tu email]
