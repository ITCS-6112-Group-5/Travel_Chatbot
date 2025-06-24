import os

def main():
    print("1. Streamlit version (LOCAL testing)")
    print("2. Flask version (DEPLOYMENT testing)")
    
    choice = input("Which launch version? (1 or 2): ").strip()
    
    if choice == "1":
        print("Starting Streamlit...")
        os.system('streamlit run Travel_Chatbot_App.py')
    elif choice == "2":
        print("Starting Flask...")
        print("http://localhost:5000")
        os.system('python app.py')
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()