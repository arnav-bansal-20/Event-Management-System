#!/bin/bash
set -e

echo "Compiling C Shared Library for macOS/Linux..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    clang -dynamiclib -o event_system.dylib functions.c
    echo "Created event_system.dylib"
else
    gcc -shared -fPIC -o event_system.so functions.c
    echo "Created event_system.so"
fi

echo "Compiling CLI Executable..."
clang main.c functions.c -o event_system
echo "Created event_system executable"

echo "Build Successful!"
echo "To run web app: python3 app.py"
echo "To run CLI app: ./event_system"
