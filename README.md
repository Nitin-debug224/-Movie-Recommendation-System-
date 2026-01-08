├── runtime.txt
├── Procfile
├── requirements.txt
├── __pycache__
    ├── auth.cpython-311.pyc
    ├── tmdb_client.cpython-311.pyc
    └── data_manager.cpython-311.pyc
├── .streamlit
    └── config.toml
├── users.csv
├── data_manager.py
├── feedback.csv
├── auth.py
├── tmdb_client.py
├── rl_agent.ipynb
└── app.py


/runtime.txt:
--------------------------------------------------------------------------------
1 | python-3.10.13
2 | 


--------------------------------------------------------------------------------
/Procfile:
--------------------------------------------------------------------------------
1 | web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
2 | 


--------------------------------------------------------------------------------
/requirements.txt:
--------------------------------------------------------------------------------
1 | streamlit
2 | flask
3 | pandas
4 | numpy
5 | requests
6 | scikit-learn
7 | python-dotenv
