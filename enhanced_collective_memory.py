#!/usr/bin/env python3
"""
Enhanced Collective Memory System
Implements advanced optimizations:
1. Optimized prompts for better quality
2. Intelligent insight filtering
3. Domain-specific memory specialization
4. Memory federation capabilities
"""

import os
import json
import uuid
import time
import openai
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import re
from collections import defaultdict

# Import existing memory systems
from memory_systems.base_memory import MemoryEntry, BaseMemorySystem
from memory_systems.shared_memory import SharedMemorySystem
from memory_systems.private_memory import PrivateMemorySystem

@dataclass
class EnhancedMemoryEntry(MemoryEntry):
    """Enhanced memory entry with additional metadata"""
    domain: str = "general"
    quality_score: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    context_similarity: float = 0.0
    federation_source: Optional[str] = None
    
class IntelligentInsightFilter:
    """Filters insights based on quality, relevance, and success metrics"""
    
    def __init__(self, min_quality_score: float = 0.2, max_insights: int = 5):
        self.min_quality_score = min_quality_score
        self.max_insights = max_insights
        
    def calculate_insight_quality(self, insight: str, context: str) -> float:
        """Calculate quality score for an insight"""
        quality_factors = []
        
        # Length factor (not too short, not too long)
        length_score = min(1.0, len(insight) / 200) * (1 - max(0, (len(insight) - 500) / 1000))
        quality_factors.append(length_score)
        
        # Specificity factor (contains specific terms)
        specific_terms = ['algorithm', 'pattern', 'optimization', 'error', 'solution', 'approach']
        specificity_score = sum(1 for term in specific_terms if term.lower() in insight.lower()) / len(specific_terms)
        quality_factors.append(specificity_score)
        
        # Code presence factor
        code_score = 1.0 if ('```' in insight or 'def ' in insight or 'class ' in insight) else 0.5
        quality_factors.append(code_score)
        
        # Actionability factor (contains action words)
        action_words = ['implement', 'use', 'apply', 'consider', 'avoid', 'ensure', 'check']
        action_score = min(1.0, sum(1 for word in action_words if word.lower() in insight.lower()) / 3)
        quality_factors.append(action_score)
        
        return np.mean(quality_factors)
    
    def filter_insights(self, insights: List[EnhancedMemoryEntry], context: str) -> List[EnhancedMemoryEntry]:
        """Filter and rank insights by quality and relevance"""
        # Calculate relevance scores
        for insight in insights:
            insight.quality_score = self.calculate_insight_quality(insight.content, context)
            insight.context_similarity = self._calculate_context_similarity(insight.content, context)
        
        # Filter by minimum quality
        filtered = [i for i in insights if i.quality_score >= self.min_quality_score]
        
        # Sort by combined score (quality + relevance + usage success)
        # Handle both MemoryEntry and EnhancedMemoryEntry objects
        filtered.sort(key=lambda x: (
            x.quality_score * 0.4 + 
            x.context_similarity * 0.3 + 
            getattr(x, 'success_rate', 1.0) * 0.2 + 
            min(1.0, getattr(x, 'usage_count', 0) / 10) * 0.1
        ), reverse=True)
        
        return filtered[:self.max_insights]
    
    def _calculate_context_similarity(self, insight: str, context: str) -> float:
        """Simple context similarity based on common words"""
        insight_words = set(re.findall(r'\w+', insight.lower()))
        context_words = set(re.findall(r'\w+', context.lower()))
        
        if not insight_words or not context_words:
            return 0.0
            
        intersection = insight_words.intersection(context_words)
        union = insight_words.union(context_words)
        
        return len(intersection) / len(union) if union else 0.0

class DomainSpecificMemory:
    """Manages domain-specific memory partitions"""
    
    def __init__(self, base_path: str = "memory_data/domains"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.domain_memories = {}
        
        # Define domain categories
        self.domain_patterns = {
            'algorithms': ['sort', 'search', 'tree', 'graph', 'dynamic programming', 'recursion'],
            'data_structures': ['list', 'dict', 'array', 'stack', 'queue', 'heap'],
            'string_processing': ['string', 'text', 'parse', 'regex', 'format'],
            'mathematics': ['math', 'calculation', 'formula', 'number', 'factorial', 'prime'],
            'validation': ['validate', 'check', 'verify', 'test', 'assert', 'error'],
            'optimization': ['optimize', 'efficient', 'performance', 'speed', 'memory usage']
        }
    
    def classify_domain(self, content: str) -> str:
        """Classify content into domain categories"""
        content_lower = content.lower()
        domain_scores = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = sum(1 for pattern in patterns if pattern in content_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        return 'general'
    
    def get_domain_memory(self, domain: str) -> SharedMemorySystem:
        """Get or create memory system for specific domain"""
        if domain not in self.domain_memories:
            domain_path = self.base_path / domain
            # Use clean domain name for system_id, but specify storage path
            self.domain_memories[domain] = SharedMemorySystem(
                system_id=f"domain_{domain}",
                storage_path=str(domain_path)
            )
        return self.domain_memories[domain]
    
    def store_domain_insight(self, insight: EnhancedMemoryEntry) -> bool:
        """Store insight in appropriate domain memory"""
        domain = self.classify_domain(insight.content)
        insight.domain = domain
        
        domain_memory = self.get_domain_memory(domain)
        return domain_memory.store(insight)
    
    def retrieve_domain_insights(self, query: str, agent_id: str, limit: int = 10) -> List[EnhancedMemoryEntry]:
        """Retrieve insights from relevant domains"""
        query_domain = self.classify_domain(query)
        all_insights = []
        
        # Primary domain - always try to get/create the domain memory
        try:
            primary_memory = self.get_domain_memory(query_domain)
            primary_insights = primary_memory.retrieve(query, agent_id, limit)
            all_insights.extend(primary_insights)
        except Exception as e:
            print(f"Error retrieving from {query_domain} domain: {e}")
        
        # General domain as fallback
        if query_domain != 'general':
            try:
                general_memory = self.get_domain_memory('general')
                general_insights = general_memory.retrieve(query, agent_id, limit // 2)
                all_insights.extend(general_insights)
            except Exception as e:
                print(f"Error retrieving from general domain: {e}")
        
        return all_insights[:limit]

class MemoryFederation:
    """Manages federated memory sharing between organizations/teams"""
    
    def __init__(self, federation_path: str = "memory_data/federation"):
        self.federation_path = Path(federation_path)
        self.federation_path.mkdir(parents=True, exist_ok=True)
        self.federation_config = self._load_federation_config()
    
    def _load_federation_config(self) -> Dict:
        """Load federation configuration"""
        config_file = self.federation_path / "federation_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {
            "trusted_sources": [],
            "sharing_enabled": True,
            "privacy_level": "public",  # public, protected, private
            "quality_threshold": 0.7
        }
    
    def export_insights(self, insights: List[EnhancedMemoryEntry], organization_id: str) -> str:
        """Export insights for federation sharing"""
        export_data = {
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat(),
            "insights": []
        }
        
        for insight in insights:
            if insight.quality_score >= self.federation_config["quality_threshold"]:
                export_data["insights"].append({
                    "content": insight.content,
                    "domain": insight.domain,
                    "quality_score": insight.quality_score,
                    "success_rate": insight.success_rate,
                    "tags": insight.tags,
                    "metadata": insight.metadata
                })
        
        export_file = self.federation_path / f"export_{organization_id}_{int(time.time())}.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return str(export_file)
    
    def import_insights(self, import_file: str, target_memory: DomainSpecificMemory) -> int:
        """Import insights from federated source"""
        with open(import_file, 'r') as f:
            import_data = json.load(f)
        
        imported_count = 0
        for insight_data in import_data["insights"]:
            insight = EnhancedMemoryEntry(
                id=str(uuid.uuid4()),
                content=insight_data["content"],
                agent_id="federated",
                timestamp=datetime.now(),
                tags=insight_data["tags"],
                metadata=insight_data["metadata"],
                domain=insight_data["domain"],
                quality_score=insight_data["quality_score"],
                success_rate=insight_data["success_rate"],
                federation_source=import_data["organization_id"]
            )
            
            if target_memory.store_domain_insight(insight):
                imported_count += 1
        
        return imported_count

class OptimizedPromptManager:
    """Manages optimized prompts for different scenarios"""
    
    def __init__(self):
        self.prompt_templates = {
            "with_insights": """
You are a {role} working on a software development task. You have access to relevant insights from previous similar tasks.

TASK: {task_description}

RELEVANT INSIGHTS FROM COLLECTIVE MEMORY:
{formatted_insights}

INSTRUCTIONS:
1. Carefully review the insights above - they contain valuable lessons from previous similar tasks
2. Apply relevant patterns and avoid known pitfalls mentioned in the insights
3. Build upon successful approaches while adapting them to this specific task
4. Focus on producing high-quality, well-tested code
5. If insights suggest specific testing approaches, implement them

Your response should be practical, actionable, and incorporate the collective wisdom while being tailored to this specific task.
""",
            
            "without_insights": """
You are a {role} working on a software development task.

TASK: {task_description}

INSTRUCTIONS:
1. Analyze the task requirements carefully
2. Design a robust, well-tested solution
3. Follow best practices for code quality and maintainability
4. Include appropriate error handling and edge case considerations
5. Provide clear, documented code

Your response should be practical, actionable, and demonstrate expertise in your role.
""",
            
            "insight_extraction": """
Based on your work on this task, identify the most valuable insights that could help in future similar tasks.

TASK COMPLETED: {task_description}
YOUR SOLUTION: {solution}
OUTCOME: {outcome}

Extract 2-3 key insights that would be valuable for future tasks. Focus on:
1. Successful patterns or approaches that worked well
2. Common pitfalls or errors to avoid
3. Testing strategies that proved effective
4. Design decisions that had positive impact

Format each insight as a clear, actionable statement that another developer could apply.
"""
        }
    
    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        """Get optimized prompt for specific scenario"""
        template = self.prompt_templates.get(prompt_type, "")
        return template.format(**kwargs)
    
    def format_insights(self, insights: List[EnhancedMemoryEntry]) -> str:
        """Format insights for inclusion in prompts"""
        if not insights:
            return "No relevant insights available from previous tasks."
        
        formatted = []
        for i, insight in enumerate(insights, 1):
            # Handle both MemoryEntry and EnhancedMemoryEntry objects
            domain = getattr(insight, 'domain', 'GENERAL')
            source_info = f"[{domain.upper()}]"
            
            federation_source = getattr(insight, 'federation_source', None)
            if federation_source:
                source_info += f" (from {federation_source})"
            
            quality_score = getattr(insight, 'quality_score', 0.0)
            success_rate = getattr(insight, 'success_rate', 1.0)
            
            formatted.append(f"""
{i}. {source_info} Quality: {quality_score:.2f}, Success Rate: {success_rate:.2f}
   {insight.content}
""")
        
        return "\n".join(formatted)

class EnhancedCollectiveMemoryAgent:
    """Enhanced agent with all optimization features"""
    
    def __init__(self, role: str, agent_id: str = None):
        self.role = role
        self.agent_id = agent_id or f"{role}_{uuid.uuid4().hex[:8]}"
        
        # Initialize enhanced components
        self.insight_filter = IntelligentInsightFilter()
        self.domain_memory = DomainSpecificMemory()
        self.federation = MemoryFederation()
        self.prompt_manager = OptimizedPromptManager()
        
        # Traditional memory systems for compatibility
        self.shared_memory = SharedMemorySystem("enhanced_shared")
        self.private_memory = PrivateMemorySystem("enhanced_private", self.agent_id, "memory_data/private")
        
        # Performance tracking
        self.performance_history = []
    
    def solve_task_with_enhanced_memory(self, task_description: str) -> Dict[str, Any]:
        """Solve task using enhanced collective memory system"""
        start_time = time.time()
        
        # 1. Retrieve relevant insights with intelligent filtering
        raw_insights = self.domain_memory.retrieve_domain_insights(
            task_description, self.agent_id, limit=20
        )
        
        # 2. Apply intelligent filtering
        filtered_insights = self.insight_filter.filter_insights(raw_insights, task_description)
        
        # 3. Generate optimized prompt
        if filtered_insights:
            prompt = self.prompt_manager.get_prompt(
                "with_insights",
                role=self.role,
                task_description=task_description,
                formatted_insights=self.prompt_manager.format_insights(filtered_insights)
            )
        else:
            prompt = self.prompt_manager.get_prompt(
                "without_insights",
                role=self.role,
                task_description=task_description
            )
        
        # 4. Get LLM response
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1
            )
            solution = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = tokens_used * 0.00045  # GPT-4 pricing
            
        except Exception as e:
            print(f"API Error: {e}")
            solution = f"Error generating solution: {e}"
            tokens_used = 0
            cost = 0.0
        
        # 5. Extract and store new insights
        self._extract_and_store_insights(task_description, solution, filtered_insights)
        
        # 6. Update performance tracking
        execution_time = time.time() - start_time
        self.performance_history.append({
            "task": task_description,
            "insights_used": len(filtered_insights),
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "cost": cost
        })
        
        return {
            "solution": solution,
            "insights_used": len(filtered_insights),
            "insights_details": [
                {
                    "content": insight.content[:100] + "...",
                    "domain": getattr(insight, 'domain', 'general'),
                    "quality": getattr(insight, 'quality_score', 0.0),
                    "source": getattr(insight, 'federation_source', None) or "local"
                }
                for insight in filtered_insights
            ],
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "cost": cost
        }
    
    def _extract_and_store_insights(self, task: str, solution: str, used_insights: List[EnhancedMemoryEntry]):
        """Extract insights from completed task and store them"""
        # Generate insight extraction prompt
        extraction_prompt = self.prompt_manager.get_prompt(
            "insight_extraction",
            task_description=task,
            solution=solution,
            outcome="completed"  # Could be enhanced with actual outcome evaluation
        )
        
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=500,
                temperature=0.2
            )
            
            insights_text = response.choices[0].message.content
            
            # Parse and store insights
            insight_lines = [line.strip() for line in insights_text.split('\n') if line.strip()]
            
            for line in insight_lines:
                if len(line) > 50:  # Filter out short/non-meaningful lines
                    insight = EnhancedMemoryEntry(
                        id=str(uuid.uuid4()),
                        content=line,
                        agent_id=self.agent_id,
                        timestamp=datetime.now(),
                        tags=[self.role, "extracted_insight"],
                        metadata={
                            "source_task": task,
                            "extraction_method": "llm_generated"
                        },
                        quality_score=self.insight_filter.calculate_insight_quality(line, task)
                    )
                    
                    # Store in domain-specific memory
                    self.domain_memory.store_domain_insight(insight)
                    
                    # Also store in traditional memory for compatibility
                    self.shared_memory.store(insight)
        
        except Exception as e:
            print(f"Insight extraction error: {e}")
        
        # Update success rates for used insights
        for insight in used_insights:
            # Handle both MemoryEntry and EnhancedMemoryEntry objects
            if hasattr(insight, 'usage_count'):
                insight.usage_count += 1
                # Simple success rate update (could be enhanced with actual outcome evaluation)
                if hasattr(insight, 'success_rate'):
                    insight.success_rate = (insight.success_rate * (insight.usage_count - 1) + 1.0) / insight.usage_count

def run_enhanced_experiment():
    """Run experiment with enhanced collective memory system"""
    print("🚀 Enhanced Collective Memory Experiment")
    print("=" * 60)
    
    # Load test problems
    from human_eval.data import read_problems
    problems = read_problems()
    test_problems = list(problems.items())[:5]  # Test with 5 problems
    
    # Initialize enhanced agents
    agents = {
        "product_manager": EnhancedCollectiveMemoryAgent("product_manager"),
        "architect": EnhancedCollectiveMemoryAgent("architect"), 
        "engineer": EnhancedCollectiveMemoryAgent("engineer"),
        "qa_engineer": EnhancedCollectiveMemoryAgent("qa_engineer")
    }
    
    results = []
    
    for i, (task_id, problem) in enumerate(test_problems, 1):
        print(f"\n[{i}/{len(test_problems)}] Processing {task_id}")
        print(f"Problem: {problem['prompt'][:100]}...")
        
        task_results = {"task_id": task_id, "problem": problem["prompt"]}
        
        # Run each agent
        for role, agent in agents.items():
            print(f"  🤖 Running {role} with enhanced memory...")
            result = agent.solve_task_with_enhanced_memory(problem["prompt"])
            task_results[role] = result
        
        results.append(task_results)
        
        # Show progress
        total_insights = sum(task_results[role]["insights_used"] for role in agents.keys())
        total_cost = sum(task_results[role]["cost"] for role in agents.keys())
        print(f"  ✅ Completed - Insights used: {total_insights}, Cost: ${total_cost:.4f}")
    
    # Save results
    output_file = "enhanced_memory_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Enhanced experiment completed! Results saved to {output_file}")
    
    # Generate summary
    print("\n📊 ENHANCED SYSTEM SUMMARY:")
    print("-" * 40)
    
    total_insights_used = sum(
        sum(task[role]["insights_used"] for role in agents.keys())
        for task in results
    )
    
    total_cost = sum(
        sum(task[role]["cost"] for role in agents.keys())
        for task in results
    )
    
    print(f"Total insights utilized: {total_insights_used}")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Average insights per task: {total_insights_used / len(results):.1f}")
    print(f"Average cost per task: ${total_cost / len(results):.4f}")
    
    # Show domain distribution
    domain_counts = defaultdict(int)
    for agent in agents.values():
        for domain in agent.domain_memory.domain_memories.keys():
            domain_counts[domain] += 1
    
    print(f"\nDomain specialization:")
    for domain, count in domain_counts.items():
        print(f"  {domain}: {count} specialized memories")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        exit(1)
    
    run_enhanced_experiment()
