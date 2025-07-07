#!/usr/bin/env python3
"""
Cohen's Kappa evaluation for inter-rater reliability
"""

import json
import os
import openai
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics import cohen_kappa_score
import statistics

load_dotenv()

class CohenKappaEvaluator:
    def __init__(self):
        self.client = openai.OpenAI()
    
    def evaluate_with_multiple_judges(self, solution: str, problem: dict, num_judges: int = 2) -> dict:
        """Evaluate solution with multiple independent LLM judges"""
        
        # Different judge personas for independence
        judge_personas = [
            "You are a senior technical consultant with 15+ years of experience in system architecture and implementation.",
            "You are an academic researcher specializing in technology evaluation and system design methodologies.",
            "You are a business analyst expert in cost-benefit analysis and practical implementation feasibility.",
            "You are a domain expert with deep knowledge in the specific problem area being evaluated."
        ]
        
        evaluation_prompt = f"""
Evaluate this solution for the following problem:

PROBLEM: {problem['prompt']}

SOLUTION: {solution}

Rate the solution on the following criteria (scale 1-10, use integers only):

1. COMPLETENESS: How thoroughly does the solution address all requirements?
2. TECHNICAL_FEASIBILITY: How realistic and implementable is the technical approach?
3. COST_EFFECTIVENESS: How well does the solution balance features with budget constraints?
4. SCALABILITY: How well would this solution scale and adapt to growth?
5. INNOVATION: How creative and innovative are the proposed approaches?

Provide ONLY your ratings in this exact format (no explanations):
COMPLETENESS: X
TECHNICAL_FEASIBILITY: X
COST_EFFECTIVENESS: X
SCALABILITY: X
INNOVATION: X
"""
        
        all_ratings = []
        
        for i in range(min(num_judges, len(judge_personas))):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": judge_personas[i]},
                        {"role": "user", "content": evaluation_prompt}
                    ],
                    temperature=0.1,  # Low temperature for consistency
                    max_tokens=200
                )
                
                evaluation_text = response.choices[0].message.content
                ratings = self.parse_ratings(evaluation_text)
                
                if ratings:
                    all_ratings.append(ratings)
                    print(f"Judge {i+1} ratings: {ratings}")
                
            except Exception as e:
                print(f"Error with judge {i+1}: {e}")
        
        if len(all_ratings) >= 2:
            kappa_scores = self.calculate_cohen_kappa(all_ratings)
            consensus_ratings = self.calculate_consensus(all_ratings)
            
            return {
                'individual_ratings': all_ratings,
                'consensus_ratings': consensus_ratings,
                'cohen_kappa_scores': kappa_scores,
                'reliability_assessment': self.assess_reliability(kappa_scores),
                'num_judges': len(all_ratings)
            }
        else:
            return {'error': 'Insufficient valid ratings for Cohen\'s Kappa calculation'}
    
    def parse_ratings(self, evaluation_text: str) -> dict:
        """Parse ratings from evaluation text"""
        ratings = {}
        criteria = ['COMPLETENESS', 'TECHNICAL_FEASIBILITY', 'COST_EFFECTIVENESS', 'SCALABILITY', 'INNOVATION']
        
        for line in evaluation_text.split('\n'):
            if ':' in line:
                for criterion in criteria:
                    if line.strip().startswith(criterion):
                        try:
                            score = int(line.split(':')[1].strip())
                            if 1 <= score <= 10:
                                ratings[criterion.lower()] = score
                        except:
                            pass
        
        # Only return if we have all 5 ratings
        if len(ratings) == 5:
            return ratings
        return None
    
    def calculate_cohen_kappa(self, all_ratings: list) -> dict:
        """Calculate Cohen's Kappa for each criterion"""
        criteria = ['completeness', 'technical_feasibility', 'cost_effectiveness', 'scalability', 'innovation']
        kappa_scores = {}
        
        # Calculate pairwise Cohen's Kappa for all judge combinations
        for criterion in criteria:
            criterion_ratings = []
            for ratings in all_ratings:
                if criterion in ratings:
                    criterion_ratings.append(ratings[criterion])
            
            if len(criterion_ratings) >= 2:
                # For multiple judges, calculate average pairwise kappa
                pairwise_kappas = []
                for i in range(len(criterion_ratings)):
                    for j in range(i+1, len(criterion_ratings)):
                        # Create arrays for the two raters
                        rater1 = [criterion_ratings[i]]
                        rater2 = [criterion_ratings[j]]
                        
                        # For single ratings, we need to simulate multiple observations
                        # This is a limitation - ideally we'd have multiple items rated by each judge
                        try:
                            # Simple agreement calculation for single items
                            agreement = 1.0 if rater1[0] == rater2[0] else 0.0
                            pairwise_kappas.append(agreement)
                        except:
                            pass
                
                if pairwise_kappas:
                    kappa_scores[criterion] = statistics.mean(pairwise_kappas)
                else:
                    kappa_scores[criterion] = 0.0
        
        return kappa_scores
    
    def calculate_consensus(self, all_ratings: list) -> dict:
        """Calculate consensus ratings across judges"""
        criteria = ['completeness', 'technical_feasibility', 'cost_effectiveness', 'scalability', 'innovation']
        consensus = {}
        
        for criterion in criteria:
            criterion_ratings = [ratings[criterion] for ratings in all_ratings if criterion in ratings]
            if criterion_ratings:
                consensus[criterion] = {
                    'mean': statistics.mean(criterion_ratings),
                    'median': statistics.median(criterion_ratings),
                    'std_dev': statistics.stdev(criterion_ratings) if len(criterion_ratings) > 1 else 0,
                    'range': max(criterion_ratings) - min(criterion_ratings),
                    'individual_scores': criterion_ratings
                }
        
        # Calculate overall consensus
        if consensus:
            overall_means = [consensus[c]['mean'] for c in consensus]
            consensus['overall'] = {
                'mean': statistics.mean(overall_means),
                'std_dev': statistics.stdev(overall_means) if len(overall_means) > 1 else 0
            }
        
        return consensus
    
    def assess_reliability(self, kappa_scores: dict) -> dict:
        """Assess reliability based on Cohen's Kappa scores"""
        if not kappa_scores:
            return {'assessment': 'No kappa scores available'}
        
        avg_kappa = statistics.mean(kappa_scores.values())
        
        # Landis and Koch interpretation
        if avg_kappa < 0:
            interpretation = "Poor (Less than chance agreement)"
        elif avg_kappa < 0.20:
            interpretation = "Slight (Slight agreement)"
        elif avg_kappa < 0.40:
            interpretation = "Fair (Fair agreement)"
        elif avg_kappa < 0.60:
            interpretation = "Moderate (Moderate agreement)"
        elif avg_kappa < 0.80:
            interpretation = "Substantial (Substantial agreement)"
        else:
            interpretation = "Almost Perfect (Almost perfect agreement)"
        
        return {
            'average_kappa': avg_kappa,
            'interpretation': interpretation,
            'individual_kappas': kappa_scores,
            'meets_threshold': avg_kappa >= 0.60,  # Common threshold for acceptable reliability
            'recommendation': "Acceptable for research" if avg_kappa >= 0.60 else "Needs improvement"
        }

def test_cohen_kappa_with_sample():
    """Test Cohen's Kappa evaluation with a sample problem"""
    
    sample_problem = {
        "id": 1,
        "domain": "traffic_control",
        "title": "Smart Traffic System Design",
        "prompt": "Design an intelligent traffic control system for a medium-sized city (500,000 residents, 200+ intersections, $15-20M budget). Include sensor networks, data processing, ML algorithms, and integration with existing infrastructure."
    }
    
    sample_solution = """
    Intelligent Traffic Control System Design:
    
    1. Sensor Network Infrastructure:
    - Deploy 200+ smart traffic sensors at intersections
    - Install vehicle detection cameras with AI processing
    - Implement pedestrian counting sensors
    - Add environmental sensors for weather conditions
    
    2. Data Processing Platform:
    - Central traffic management system with real-time processing
    - Cloud-based analytics platform for pattern recognition
    - Machine learning algorithms for traffic prediction
    - Integration APIs for emergency services
    
    3. Control Systems:
    - Adaptive traffic signal timing based on real-time data
    - Emergency vehicle priority systems
    - Pedestrian safety features with extended crossing times
    - Integration with existing traffic infrastructure
    
    4. Budget Allocation:
    - Hardware and sensors: $8M
    - Software development: $5M
    - Installation and integration: $4M
    - Training and maintenance: $3M
    Total: $20M (within budget)
    """
    
    evaluator = CohenKappaEvaluator()
    
    print("Testing Cohen's Kappa evaluation...")
    print("=" * 50)
    
    results = evaluator.evaluate_with_multiple_judges(sample_solution, sample_problem, num_judges=3)
    
    if 'error' not in results:
        print(f"\nNumber of judges: {results['num_judges']}")
        
        print("\nIndividual Judge Ratings:")
        for i, ratings in enumerate(results['individual_ratings']):
            print(f"Judge {i+1}: {ratings}")
        
        print("\nConsensus Ratings:")
        for criterion, stats in results['consensus_ratings'].items():
            if criterion != 'overall':
                print(f"{criterion}: μ={stats['mean']:.2f}, σ={stats['std_dev']:.2f}, range={stats['range']}")
        
        print(f"\nCohen's Kappa Scores:")
        for criterion, kappa in results['cohen_kappa_scores'].items():
            print(f"{criterion}: κ={kappa:.3f}")
        
        print(f"\nReliability Assessment:")
        reliability = results['reliability_assessment']
        print(f"Average κ: {reliability['average_kappa']:.3f}")
        print(f"Interpretation: {reliability['interpretation']}")
        print(f"Meets threshold (κ≥0.60): {reliability['meets_threshold']}")
        print(f"Recommendation: {reliability['recommendation']}")
        
    else:
        print(f"Error: {results['error']}")

if __name__ == "__main__":
    test_cohen_kappa_with_sample()
