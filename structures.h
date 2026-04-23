#ifndef STRUCTURES_H
#define STRUCTURES_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define TABLE_SIZE 100
#define HEAP_SIZE 100
#define MAX_NAME 100
#define MAX_DESC 256
typedef struct Participant
{
  int id;
  char name[MAX_NAME];
  struct Participant *next;
} Participant;
typedef struct Event
{
  int id;
  char name[MAX_NAME];
  int priority;
  char description[MAX_DESC];
  char date[20];
  Participant *participants;
  struct Event *nextHash;
} Event;
typedef struct System
{
  Event *eventHashTable[TABLE_SIZE];
  Event *eventHeap[HEAP_SIZE];
  int heapSize;
} System;
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif
EXPORT void initSystem(System *sys);
EXPORT void clearSystem(System *sys);
unsigned int hash(char *name);
EXPORT int addEvent(System *sys, int id, char *name, int priority, char *desc, char *date);
EXPORT Event *searchEvent(System *sys, char *name);
EXPORT int deleteEventByName(System *sys, char *name);    
EXPORT int getNextId(System *sys);
EXPORT Event *getNextEvent(System *sys);
EXPORT void getNextHighPriorityEvents(System *sys, Event **buffer, int *count);
EXPORT void printEvent(Event *e);
EXPORT void addParticipant(System *sys, char *eventName, int pID, char *pName);
EXPORT void listParticipants(Event *e);
EXPORT void displayAllEvents(System *sys);
EXPORT void getAllEvents(System *sys, Event *buffer, int *count); 
EXPORT void saveSystemToFile(System *sys, const char *filename);
EXPORT void loadSystemFromFile(System *sys, const char *filename);
#endif