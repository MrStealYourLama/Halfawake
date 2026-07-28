
from config import ASSISTANT_NAME, VERSION
from utils.logger import setup_logger
from agent.brain import Brain
from agent.conversation import Conversation
from agent.memory import Memory

def main():

    logger = setup_logger()

    print("=" * 40)
    print(f"{ASSISTANT_NAME} {VERSION}")
    print("=" * 40)
    print('')
    print('Typing "exit", "quit" or "tschüss" will end the conversation.')

    brain = Brain()
    memory = Memory()
    conversation = Conversation(brain, memory)


    while True:

        user = input("\nDu: ")

        if user.lower() in ["exit", "quit", "tschüss"]:
            print("JARVIS: Bis später!")
            break

        answer = conversation.ask(user)

        print(f"\nJARVIS: {answer}")


if __name__ == "__main__":
    main()
