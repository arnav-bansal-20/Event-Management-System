#include "structures.h"

void displayMenu() {
  printf("\n========================================\n");
  printf("        EVENT MANAGEMENT SYSTEM         \n");
  printf("========================================\n");
  printf("1. Add New Event\n");
  printf("2. Search Event by Name\n");
  printf("3. Delete Event by Name\n");
  printf("4. Display All Events\n");
  printf("5. View Highest Priority Event\n");
  printf("6. Add Participant to Event\n");
  printf("7. Save to Database\n");
  printf("8. Load from Database\n");
  printf("0. Exit\n");
  printf("----------------------------------------\n");
  printf("Enter your choice: ");
}

int main() {
  System sys;
  initSystem(&sys);
  const char *dbFile = "events.db";

  loadSystemFromFile(&sys, dbFile);

  int choice;
  char name[MAX_NAME];
  char desc[MAX_DESC];
  char date[20];
  char pName[MAX_NAME];
  int priority, pId;

  while (1) {
    displayMenu();
    if (scanf("%d", &choice) != 1) {
      while (getchar() != '\n'); // clear buffer
      printf("Invalid input. Please enter a number.\n");
      continue;
    }
    while (getchar() != '\n'); // consume newline

    switch (choice) {
      case 1: {
        printf("\n--- Add New Event ---\n");
        printf("Enter Event Name: ");
        fgets(name, sizeof(name), stdin);
        name[strcspn(name, "\n")] = 0;

        printf("Enter Priority (1-100, lower is higher priority): ");
        if (scanf("%d", &priority) != 1) {
          while (getchar() != '\n');
          printf("Invalid priority.\n");
          break;
        }
        while (getchar() != '\n');

        printf("Enter Description: ");
        fgets(desc, sizeof(desc), stdin);
        desc[strcspn(desc, "\n")] = 0;

        printf("Enter Date (YYYY-MM-DD): ");
        fgets(date, sizeof(date), stdin);
        date[strcspn(date, "\n")] = 0;

        int newId = getNextId(&sys);
        if (addEvent(&sys, newId, name, priority, desc, date)) {
          saveSystemToFile(&sys, dbFile);
        }
        break;
      }
      case 2: {
        printf("\n--- Search Event ---\n");
        printf("Enter Event Name: ");
        fgets(name, sizeof(name), stdin);
        name[strcspn(name, "\n")] = 0;

        Event *e = searchEvent(&sys, name);
        if (e) {
          printf("\nEvent Found:\n");
          printEvent(e);
        } else {
          printf("Event '%s' not found.\n", name);
        }
        break;
      }
      case 3: {
        printf("\n--- Delete Event ---\n");
        printf("Enter Event Name to Delete: ");
        fgets(name, sizeof(name), stdin);
        name[strcspn(name, "\n")] = 0;

        if (deleteEventByName(&sys, name)) {
          saveSystemToFile(&sys, dbFile);
        }
        break;
      }
      case 4:
        displayAllEvents(&sys);
        break;
      case 5: {
        printf("\n--- Highest Priority Event ---\n");
        Event *next = getNextEvent(&sys);
        if (next) {
          printEvent(next);
        } else {
          printf("No events currently scheduled.\n");
        }
        break;
      }
      case 6: {
        printf("\n--- Add Participant ---\n");
        printf("Enter Event Name: ");
        fgets(name, sizeof(name), stdin);
        name[strcspn(name, "\n")] = 0;

        printf("Enter Participant ID: ");
        if (scanf("%d", &pId) != 1) {
          while (getchar() != '\n');
          printf("Invalid ID.\n");
          break;
        }
        while (getchar() != '\n');

        printf("Enter Participant Name: ");
        fgets(pName, sizeof(pName), stdin);
        pName[strcspn(pName, "\n")] = 0;

        addParticipant(&sys, name, pId, pName);
        saveSystemToFile(&sys, dbFile);
        break;
      }
      case 7:
        saveSystemToFile(&sys, dbFile);
        break;
      case 8:
        clearSystem(&sys);
        loadSystemFromFile(&sys, dbFile);
        break;
      case 0:
        saveSystemToFile(&sys, dbFile);
        clearSystem(&sys);
        printf("Goodbye!\n");
        return 0;
      default:
        printf("Invalid choice. Please try again.\n");
    }
  }

  return 0;
}
