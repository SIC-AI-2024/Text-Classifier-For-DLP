# Text Classifier for Data Loss Prevention (DLP)

This project implements a two-stage text classifier for data loss prevention. The first classifier distinguishes between enterprise and non-enterprise data, while the second classifier further categorizes enterprise documents as sensitive or safe. Support Vector Machines (SVM) and Long Short-Term Memory networks (LSTM) are employed for model building. The backend is built using FastAPI and Python, while the frontend is a React application.

---

## Project Structure

The project is organized as follows:

* **Backend:** Contains the FastAPI backend code, including the API endpoints for text classification. The `requirement.txt` file lists the necessary Python packages.  The trained models (SVM and LSTM) are located in the `/models` directory within the `Backend` directory.
* **Frontend (dlp):** Contains the React application for user interaction and displaying classification results.

---

## Installation

### Backend

1. **Navigate to the Backend directory:** 
    ```bash 
    cd Backend
    ```
2. **Create and activate a virtual environment (recommended):** 
    * **Create**
        ```bash
        python3 -m venv .venv
        ```
        Or, depending on your setup 
        ```bash
        python -m venv .venv
        ``` 
    * **Activate**
        ```bash
        source .venv/bin/activate
        ``` 
        Or, on Windows
        ```bash
        .venv\Scripts\activate
        ``` 
3. **Install dependencies:** 
    ```bash
    pip install -r requirement.txt
    ```
4. **(If necessary) Install additional dependencies:** Depending on your specific model dependencies and the contents of `requirement.txt`, you might need to install additional packages (e.g., scikit-learn, tensorflow/keras).

5. **Run the FastAPI server:** 
    ```bash
    uvicorn main:app --reload
    ```
    replace `main:app` with the correct module and app variable name if different.

---

### Frontend

1. **Navigate to the Frontend directory:** 
    ```bash
    cd ../dlp
    ```
2. **Install Node.js and npm (or yarn):** Download from [https://nodejs.org/](https://nodejs.org/).

3. **Install frontend dependencies:** 
    ```bash
    npm install
    ```
    Or,
    ```bash
    yarn install
    ```
4. **Start the React development server:** 
    ```bash
    npm start
    ```
    Or,
    ```bash
    yarn start
    ```

---

## Usage

Once both the backend and frontend servers are running, the React application will communicate with the FastAPI backend to perform text classification. The user interface will allow inputting text, and the results (enterprise/non-enterprise and sensitive/safe classifications) will be displayed.

---

## Model Details

* **Classifier 1 (Enterprise vs. Non-Enterprise):** Uses an SVM model trained on [Describe the dataset used].
* **Classifier 2 (Sensitive vs. Safe):** Uses an SVM model trained on [Describe the dataset used, specifying that it's a subset of enterprise data].  Note: While both SVM and LSTM models may exist in the `/models` directory, the application currently utilizes only the SVM model for both classification stages.

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

