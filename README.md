# Financial Reconciliation Agent

## Overview
This project implements an AI-driven **Financial Reconciliation Agent** that processes transactional data to:
- Identify unresolved cases and suggest next steps.
- Detect resolution patterns to automate future issue resolutions.
- Generate consolidated reports using **Ollama's Llama model**.

## Features
- **Data Preprocessing**: Cleans and formats input reconciliation data.
- **Categorization of Unmatched Transactions**: Identifies `Not Found-SysB` cases.
- **Resolution Analysis**: Uses LLM to classify cases as `resolved` or `unresolved`, along with reasons and next steps.
- **Automated Pattern Recognition**: Extracts resolution patterns from past cases.
- **Final Consolidated Report**: Provides a summary of resolved/unresolved cases with actionable insights.

---
## Folder Structure
```
fin-reconciliation-agent/
│── data/                  # Folder for input CSV files
│── reports/               # Folder for generated reports
│── uploads/               # Folder for uploaded output files
│── src/                   # Source code directory
│   │── reconciliation_agent.py  # Core logic for reconciliation agent
│   │── main.py                 # Main script to run the agent
│── README.md               # Project documentation
│── requirements.txt        # List of dependencies
```

---
## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Git
- Ollama (for running local Llama models)

### Clone the Repository
```sh
git clone https://github.com/vshilpi/fin-reconciliation-agent.git
cd fin-reconciliation-agent
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Install and Run Ollama
1. Download and install Ollama from: [Ollama.ai](https://ollama.ai)
2. Pull the required Llama model:
   ```sh
   ollama pull llama3
   ```
3. Start the Ollama service:
   ```sh
   ollama run llama3
   ```

---
## Usage
### Running the Reconciliation Agent
```sh
python src/main.py
```

### Input Data
- Place raw reconciliation data (`recon_sample_raw.csv`) and responses (`recon_sample_reply.csv`) inside the `data/` folder.

### Output
- Processed reports will be saved in the `reports/` folder.
- `not_found_sysb.csv` will be saved in the `uploads/` folder.
- Console logs will display analysis summaries.

---
## Example Output
Sample JSON output from LLM analysis:
```json
{
    "status": "resolved",
    "reason": "Transaction was correctly processed.",
    "next_steps": ["Close ticket", "Update records"]
}
```

---
## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a Pull Request.



