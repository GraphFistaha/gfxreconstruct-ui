# gfxreconstruct-ui
gfxreconstruct - application to record all vulkan/directX commands to debug graphics application and analize them.
The problem is gfxreconstruct generates json, and it's hard to read and analize. So I've created this GUI application for gfxreconstruct. It's inspired by https://github.com/apitrace/apitrace and works the same way. The main goal - to show you a plate table with all recorded commands.

Right now it can two things:
- capture trace (File - Capture - (set path to application) - Run) - launchs application, record all commands and save it in .gfxr file
- Open trace (File - open trace - select .gfxr file - Open) - shows all vulkan commands from .gfxr file
I've heard, gfxreconstruct can work with DirectX12, but I have no application to test it. Probably later.

The application's main window is separated on two parts: the table with commands and details window of one command. Select row to show details of command

I used python and tkinter because it's easy to use and easy to change.

# How it's look like:
<img width="1002" height="815" alt="image" src="https://github.com/user-attachments/assets/09dafc5c-160e-4bbf-8027-6049406dc468" />

