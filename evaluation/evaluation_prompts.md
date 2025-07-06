# Evaluation Prompts for Multi-LLM Collective Memory Research

## Core Benchmark Task

### Primary Task Prompt

```
Design an intelligent traffic control system using sensors, edge computing, and AI-based prediction for a medium-sized city (population ~500,000). Your solution must address the following requirements:

**System Requirements:**
1. Handle 200+ intersections across the city
2. Support real-time decision making with <100ms response time
3. Achieve 20-30% reduction in average travel times
4. Integrate with existing city infrastructure
5. Ensure 99.5%+ system uptime

**Deliverables Required:**
1. **System Architecture**: Overall design, component integration, data flow
2. **Hardware Specifications**: Sensor types, deployment strategy, networking
3. **AI/ML Architecture**: Prediction models, training strategy, inference pipeline
4. **Implementation Plan**: Phased rollout, timeline, resource requirements
5. **Evaluation Framework**: Success metrics, monitoring, validation methodology

**Constraints:**
- Budget: $15-20M total investment
- Timeline: 36 months for full deployment
- Existing infrastructure: Legacy traffic signals, city network, operations center
- Regulatory: Must comply with traffic safety standards and data privacy laws

**Success Criteria:**
- Technical feasibility and innovation
- Integration coherence across components
- Implementation practicality
- Measurable performance improvements
- Cost-effectiveness and ROI

Provide a comprehensive solution that demonstrates deep technical understanding and practical implementation considerations.
```

## Agent-Specific Sub-Prompts

### System Architect Agent
```
As a System Architect, focus on:
- High-level system design and architecture patterns
- Component integration and interfaces
- Scalability and reliability considerations
- Technology stack selection and rationale
- System-wide constraints and trade-offs

Consider: microservices vs monolithic, edge-cloud hybrid, fault tolerance, security architecture.
```

### Sensor Expert Agent
```
As a Sensor Hardware Expert, focus on:
- Sensor technology selection (cameras, radar, lidar, inductive loops)
- Deployment topology and coverage optimization
- Hardware specifications and environmental considerations
- Network architecture for sensor communication
- Maintenance and calibration strategies

Consider: cost-performance trade-offs, weather resistance, power management, data transmission.
```

### ML Engineer Agent
```
As an ML Engineer, focus on:
- Traffic prediction algorithms and model architecture
- Real-time inference requirements and optimization
- Training data strategy and model updates
- Performance metrics and accuracy targets
- Edge computing vs cloud processing decisions

Consider: LSTM for time series, computer vision for traffic analysis, reinforcement learning for optimization.
```

### Implementation Planner Agent
```
As an Implementation Planner, focus on:
- Phased deployment strategy and risk mitigation
- Resource allocation and project timeline
- Stakeholder coordination and change management
- Budget planning and cost optimization
- Quality assurance and testing protocols

Consider: pilot programs, gradual rollout, training requirements, integration challenges.
```

### Evaluator Agent
```
As an Evaluator, focus on:
- Key Performance Indicators (KPIs) and success metrics
- Monitoring and alerting systems
- Validation methodology and testing frameworks
- Performance benchmarking and baseline establishment
- Continuous improvement and optimization strategies

Consider: traffic flow metrics, system performance, environmental impact, economic ROI.
```

## Evaluation Rubric

### Quality Assessment Criteria

#### 1. Solution Completeness (25 points)
- **Excellent (23-25)**: All required components addressed comprehensively
- **Good (18-22)**: Most components covered with good detail
- **Fair (13-17)**: Basic coverage of main components
- **Poor (0-12)**: Missing major components or superficial treatment

#### 2. Technical Accuracy (25 points)
- **Excellent (23-25)**: Technically sound with realistic specifications
- **Good (18-22)**: Mostly accurate with minor technical issues
- **Fair (13-17)**: Generally reasonable but some questionable choices
- **Poor (0-12)**: Significant technical errors or unrealistic assumptions

#### 3. Integration Coherence (20 points)
- **Excellent (18-20)**: Components work together seamlessly
- **Good (14-17)**: Good integration with minor gaps
- **Fair (10-13)**: Basic integration but some disconnects
- **Poor (0-9)**: Poor integration or conflicting components

#### 4. Innovation and Creativity (15 points)
- **Excellent (14-15)**: Novel approaches and creative solutions
- **Good (11-13)**: Some innovative elements
- **Fair (8-10)**: Standard approaches with minor innovations
- **Poor (0-7)**: Conventional solutions without creativity

#### 5. Implementation Feasibility (15 points)
- **Excellent (14-15)**: Highly practical and implementable
- **Good (11-13)**: Feasible with reasonable effort
- **Fair (8-10)**: Possible but challenging to implement
- **Poor (0-7)**: Unrealistic or impractical to implement

### Memory System Evaluation

#### Memory Utilization Metrics
1. **Read/Write Ratio**: Balance of memory consumption vs. retrieval
2. **Cross-Agent Knowledge Sharing**: Evidence of collaborative memory use
3. **Redundancy Reduction**: Avoided re-computation of similar information
4. **Knowledge Reuse Rate**: Percentage of retrieved information that influences decisions

#### Collaboration Quality Indicators
1. **Information Building**: How agents build upon each other's contributions
2. **Conflict Resolution**: How disagreements or contradictions are handled
3. **Specialization Benefits**: Evidence of domain expertise contributing to overall quality
4. **Emergent Insights**: Ideas that emerge from agent interactions

## Human Evaluation Guidelines

### Expert Reviewer Instructions

```
You are evaluating solutions to a complex traffic control system design challenge. Please assess each solution across the five criteria above, providing:

1. **Numerical Scores**: Use the rubric to assign points for each criterion
2. **Qualitative Feedback**: Explain your reasoning for each score
3. **Comparative Assessment**: Note strengths/weaknesses relative to other solutions
4. **Implementation Viability**: Comment on real-world feasibility

**Blind Evaluation**: You will not know which configuration produced each solution. Focus purely on the quality and completeness of the technical content.

**Consistency Check**: After evaluating all solutions, review your scores for consistency and adjust if necessary.
```

### Inter-Rater Reliability Protocol

1. **Calibration Phase**: All evaluators score 2-3 sample solutions together
2. **Independent Evaluation**: Each evaluator scores all solutions independently  
3. **Consensus Discussion**: Discuss significant score differences (>5 points)
4. **Final Scoring**: Provide final scores after discussion

## Statistical Analysis Framework

### Hypothesis Testing

**H1**: Multi-agent with shared memory achieves significantly higher quality scores than baseline
- Test: One-way ANOVA with post-hoc comparisons
- Significance level: α = 0.05

**H2**: Shared memory reduces token usage by 20-40% compared to no-memory configurations
- Test: Paired t-test comparing token efficiency
- Effect size: Cohen's d

**H3**: Memory systems demonstrate measurable knowledge reuse and redundancy reduction
- Test: Descriptive statistics and correlation analysis
- Metrics: Memory utilization ratios, cross-agent access patterns

### Power Analysis

For detecting medium effect sizes (d = 0.5) with 80% power:
- Minimum sample size: n = 16 per group
- Recommended: n = 20 per group (5 iterations × 4 configurations)

## Validation Methodology

### Content Validity
- Expert review of task complexity and realism
- Alignment with real-world traffic system challenges
- Coverage of key technical domains

### Construct Validity  
- Factor analysis of evaluation criteria
- Correlation between different quality measures
- Convergent validity with existing benchmarks

### External Validity
- Generalizability to other complex reasoning tasks
- Robustness across different LLM models
- Consistency across different evaluators

---

*This evaluation framework ensures rigorous, reproducible assessment of multi-LLM collective memory systems while maintaining scientific validity and practical relevance.*
