import pandas as pd
import json
import os
from typing import List, Dict, Tuple
from datetime import datetime
from enum import Enum
from ollama import generate

class ResolutionStatus(Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
  

class ReconciliationAgent:
    def __init__(self):
        self.resolution_keywords = {
            'resolved': ['resolved', 'cleared', 'rectified', 'correct', 'processed correctly'],
            'unresolved': ['unresolved', 'missing', 'incorrect', 'error', 'investigation', 'wait']
        }

    def preprocess_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        raw_data['sys_a_date'] = pd.to_datetime(raw_data['sys_a_date'], format='%d/%m/%y')
        raw_data['recon_sub_status'] = raw_data['recon_sub_status'].apply(json.loads)
        return raw_data

    def categorize_not_found_sysb(self, data: pd.DataFrame) -> pd.DataFrame:
        not_found_sysb = data[
            data['recon_sub_status'].apply(lambda x: any('Not Found-SysB' in v for v in x.values()))
        ][['txn_ref_id', 'sys_a_amount_attribute_1', 'sys_a_date']]
        
        return not_found_sysb.rename(columns={
            'txn_ref_id': 'order_id',
            'sys_a_amount_attribute_1': 'amount',
            'sys_a_date': 'date'
        })
    
    def upload_file(self, df: pd.DataFrame, filename: str, folder: str):
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, filename)
        df.to_csv(file_path, index=False)
        print(f"File saved to {file_path}")
    
    def save_to_text(self,data, filename, folder):
        """Save textual data to a file in the specified folder."""
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(data, list):
                f.write("\n".join(data))  # Join list elements as separate lines
            else:
                f.write(data)

        print(f"File saved: {file_path}")
    
    
    def analyze_resolution(self, comment: str) -> Tuple[ResolutionStatus, str, List[str]]:
        """Analyze resolution comment using LLM and determine status, reason, and next steps."""
        
        prompt = f"""
        Analyze the following resolution comment and classify it as 'resolved' or 'unresolved'. 
        Also, provide a brief reason and suggest appropriate next steps.
        
        Comment: {comment}
        
        Respond in **ONLY** the following JSON format (without extra words):
        {{
            "status": "resolved" or "unresolved",
            "reason": "<brief reason>",
            "next_steps": ["<step1>", "<step2>", ...]
        }}
        """

        response = generate("llama3", prompt)
        response_text = response["response"]
        

        try:
            response_json = json.loads(response_text)
            
            status = ResolutionStatus.RESOLVED if response_json["status"].lower() == "resolved" else ResolutionStatus.UNRESOLVED
            reason = response_json["reason"]
            next_steps = response_json["next_steps"]
        except (json.JSONDecodeError, KeyError):
            # Fallback in case of unexpected response format
            status = ResolutionStatus.UNRESOLVED
            reason = "Could not determine reason due to response parsing error."
            next_steps = ["Manual review required"]

        return status, reason, next_steps
    
    def process_resolutions(self, sysb_data: pd.DataFrame, resolution_data: pd.DataFrame) -> Dict:
        results = {'resolved_cases': [], 'unresolved_cases': [], 'summary': {'total_cases': len(resolution_data), 'resolved_count': 0, 'unresolved_count': 0}}
        
        for _, row in resolution_data.iterrows():
            status, reason, next_steps = self.analyze_resolution(row['Comments'])
            case_info = {'order_id': row['Transaction ID'], 'amount': row['amount'], 'reason': reason, 'next_steps': next_steps}
            
            if status == ResolutionStatus.RESOLVED:
                results['resolved_cases'].append(case_info)
                results['summary']['resolved_count'] += 1
            else:
                results['unresolved_cases'].append(case_info)
                results['summary']['unresolved_count'] += 1
        
        return results
    
    def generate_unresolved_summary(self, unresolved_cases: List[Dict]) -> str:
        return f"Unresolved Cases Summary: {len(unresolved_cases)} cases remain unresolved. Details: {unresolved_cases}"
    
    def suggest_next_steps(self, unresolved_cases: List[Dict]) -> List[str]:
        return [f"For Order ID {case['order_id']}, suggested next step: {case['next_steps']}" for case in unresolved_cases]
    
    def identify_resolution_patterns(self, resolved_cases: List[Dict]) -> str:
        resolved_text = "\n".join([case['reason'] for case in resolved_cases])
        prompt = f"""Identify patterns in the following resolved cases so that it can
                    be closed internally if possible, without raising it to support:\n{resolved_text}"""
        
        response = generate("llama3", prompt)
        return response['response']
    def LLMConsolidation(self, results: Dict) -> str:
        consolidated_text = f"""Total Cases: {results['summary']['total_cases']}\nResolved: {results['summary']['resolved_count']}\nUnresolved: {results['summary']['unresolved_count']}\nUnresolved Cases Details: {results['unresolved_cases']}"""
        
        prompt = f"""Analyze the following resolution report details and generate a consolidated summary with actionable insights:\n{consolidated_text}"""
        
        response = generate("llama3", prompt)
        return response['response']
