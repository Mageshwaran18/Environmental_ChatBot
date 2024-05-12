EcoBuddy Chatbot

Project Description:

EcoBuddy is a chatbot powered by Dialogflow, designed to assist users in various environmental-related tasks. It offers several features:

-Carbon Footprint Calculator: 🌍 The chatbot can calculate the carbon footprint of individuals, providing insights into their environmental impact.

-Recycling Guidelines: ♻️ EcoBuddy provides recycling guidelines for different materials, helping users understand how to properly recycle various items.

-Reference Videos: 🎥 Users can access reference YouTube video links related to recycling and environmental conservation.

-Live Weather Updates: ☁️ EcoBuddy keeps users updated on live weather news, providing real-time information on weather conditions.

-Top Recycling Companies:🏭 The chatbot offers details about the top companies involved in recycling materials, facilitating informed choices for users interested in recycling initiatives.

-Air Quality Index (AQI) Tracking: 🏙️ Users can track the Air Quality Index (AQI) of their city, enabling them to monitor air pollution levels.

The project utilizes Dialogflow for chatbot creation and AQI retrieval. To fulfill Dialogflow's requirements and enable HTTP support, FastAPI is employed. Ngrok is utilized to convert HTTP into HTTPS for secure communication. Additionally, for user convenience, the chatbot is deployed as a Telegram bot named EcoBuddy.

Features

- Carbon footprint calculation
- Recycling guidelines for various materials
- Reference YouTube video links
- Live weather updates
- Information on top recycling companies
- Air Quality Index (AQI) tracking

Technologies Used

- Dialogflow
- FastAPI
- Ngrok
- Telegram Bot API

How to Use

1. Install the Requirements properly such as NGROK , FASTapi etc.
2. To run the Backend code use uvicorn main:app --reload
3. To convert http to https , in the cmd direct to project and run command as ngrok http 8000
4. Change the fullfillment link by ngrok generated link 
