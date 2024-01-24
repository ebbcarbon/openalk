#!/bin/bash

GIT_TOPLEVEL=$(git rev-parse --show-toplevel)

echo "Installing with repo location $GIT_TOPLEVEL"

sed "s+<REPO_LOCATION>+$GIT_TOPLEVEL+g" install/ta.desktop > $HOME/Desktop/ta.desktop

chmod a+x $HOME/Desktop/ta.desktop

echo "Installed."
