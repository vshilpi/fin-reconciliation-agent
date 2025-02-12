import pandas as pd
from src.reconciliation_agent import ReconciliationAgent
import chardet

def main():
    agent = ReconciliationAgent()
    def detect_encoding(file_path):
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']



    # Load data
    raw_data = pd.read_csv('data/recon_data_raw.csv', encoding=detect_encoding('data/recon_data_raw.csv'))
    resolution_data = pd.read_csv('data/recon_data_reply.csv',encoding=detect_encoding('data/recon_data_reply.csv'))
    
    # Preprocess data
    processed_data = agent.preprocess_data(raw_data)
    
    # Identify cases not found in System B
    sysb_cases = agent.categorize_not_found_sysb(processed_data)
    agent.upload_file(sysb_cases, 'not_found_sysb.csv', 'reports')

    # Process resolution comments and classify cases
    results = agent.process_resolutions(sysb_cases, resolution_data)

    # Generate next steps for unresolved cases
    next_steps = agent.suggest_next_steps(results['unresolved_cases'])
    agent.save_to_text(next_steps, 'unresolved_next_steps.txt', 'reports')

    # Identify resolution patterns for resolved cases
    resolution_patterns = agent.identify_resolution_patterns(results['resolved_cases'])
    agent.save_to_text(resolution_patterns, 'resolution_patterns.txt', 'reports')

    # Generate final report
    final_report = agent.LLMConsolidation(results)
    agent.save_to_text(final_report, 'final_report.txt', 'reports')

    print("Reconciliation Summary:", results)
    print("Reconciliation Final Report:", final_report)

if __name__ == "__main__":
    main()
