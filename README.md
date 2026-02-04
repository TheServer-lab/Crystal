# Crystal Shell

A simple, readable shell for Windows that uses natural language commands.

## Installation

1. Install Python 3.7 or higher
2. Install the Lark parser library:
   ```bash
   pip install lark
   ```

## Usage

### Interactive Mode
```bash
python crystal.py
```

### Run a Script
```bash
python crystal.py script.cry
```

## Language Syntax

### Comments

```crystal
# This is a comment
say "Hello" # This is also a comment

# Comments can be on their own line
# or at the end of a line
```

### Basic Commands

**Print output:**
```crystal
say "Hello World"
say "The answer is 'variable'"
```

**Get user input:**
```crystal
ask "What is your name?" local 'name'
ask "Enter password" global 'password'
```

**Pause execution:**
```crystal
pause
pause "Press Enter to continue..."
pause "Ready to delete files? Press Enter..."
```

**Variables:**
```crystal
set local 'count' = 10
set global 'username' = admin
```

### Arithmetic

```crystal
set local 'x' = 5 + 3
set local 'y' = 10 * 2
set local 'z' = (5 + 3) * 2
set local 'result' = 'x' + 'y'
```

Supported operators: `+`, `-`, `*`, `/`, `%`

### Control Flow

**If statements:**
```crystal
if 'age' greater than 18
say "You're an adult"
end if

if {file.txt} exists
say "File found!"
end if
```

**Loops:**
```crystal
# Count-based
repeat 10
say "Hello"
end repeat

# Infinite (Ctrl+C to stop)
repeat infinite
say "Forever"
end repeat

# While condition
repeat while 'count' less than 5
say "Count: 'count'"
set local 'count' = 'count' + 1
end repeat

# Until condition
repeat until 'done' equals yes
# ... do stuff
end repeat

# For each file
repeat for each 'file' in C:/temp
say "Found: 'file'"
end repeat
```

### File Operations

```crystal
# Copy files
copy file.txt to backup.txt
copy C:/folder to C:/backup

# Move files
move file.txt to C:/documents/file.txt

# Delete files (with confirmation)
delete old_file.txt
delete temp_folder

# List directory contents
list all
list files
list folders
list all in C:/temp

# Create empty files and folders
create file test.txt
create folder new_directory

# Make file with content
make file readme.txt "This is my readme file!"
make file config.txt "Setting1=Value1
Setting2=Value2"

# Make multiple folders at once (creates parent directories too)
make folder folder1 folder2 folder3
make folder C:/Users/User/Downloads/deep/nested/path
```

### Functions

Define reusable functions:

```crystal
# Define a function
function greet
say "Hello from my function!"
say "This can have multiple lines"
end function

# Call the function
greet

# Functions can use variables
set local 'name' = Sam
function say_hello
say "Hello 'name'!"
end function

say_hello
```

### Including Other Scripts

Share code between scripts:

```crystal
# Include another script
include helper.cry
include C:/scripts/utilities.cry

# The included script's variables and functions become available
# in the current script
```

### Error Handling

Handle errors gracefully:

```crystal
# Basic try-catch
try
delete important_file.txt
say "File deleted"
catch
say "Could not delete file"
end try

# Useful for network operations
try
download "https://example.com/file.txt" to file.txt
catch
say "Download failed"
end try

# Useful for file operations
try
copy source.txt to destination.txt
catch
say "Copy failed - file might not exist"
end try
```

### Network Operations

```crystal
# Ping a host
ping "google.com"
ping "8.8.8.8"
ping "192.168.1.1"

# Download files
download "https://example.com/file.txt" to myfile.txt
download "https://example.com/image.png" to C:/downloads/image.png

# Download with error handling
try
download "https://example.com/data.json" to data.json
say "Download successful!"
catch
say "Download failed"
end try
```

### Chaining Commands

```crystal
copy file.txt to backup.txt; delete file.txt; say "Done!"
```

### Comparisons

- `greater than` or `>`
- `less than` or `<`
- `equals` or `is` or `=`

## Examples

### Simple Counter
```crystal
set local 'i' = 1
repeat 5
say "Count: 'i'"
set local 'i' = 'i' + 1
end repeat
```

### File Organizer
```crystal
say "Organizing files..."
create folder organized
repeat for each 'file' in C:/downloads
copy 'file' to organized/'file'
end repeat
say "Done!"
```

### Interactive Calculator
```crystal
ask "Enter first number:" local 'a'
ask "Enter second number:" local 'b'
set local 'sum' = 'a' + 'b'
say "'a' + 'b' = 'sum'"
```

### Using Functions
```crystal
function show_menu
say "===================="
say "   Main Menu"
say "===================="
say "1. Option 1"
say "2. Option 2"
say "3. Exit"
end function

show_menu
ask "Select an option:" local 'choice'
```

### Project Setup Script
```crystal
say "Setting up project..."

make folder src src/components src/utils
make folder tests
make file src/main.py "# Main application file
print('Hello World!')"
make file README.md "# My Project
This is my awesome project!"

say "Project structure created!"
list all in src
```

### Modular Scripts with Include
```crystal
# main.cry
include utils.cry
include config.cry

say "Starting application..."
initialize
run_app
cleanup
```

### Error Handling Example
```crystal
# Backup script with error handling
function safe_backup
try
copy important.txt to backups/important.txt
say "Backup successful!"
catch
say "Backup failed - creating backup folder"
make folder backups
copy important.txt to backups/important.txt
end try
end function

safe_backup
```

### Network Automation
```crystal
# Check if servers are online
say "Checking servers..."

ping "server1.example.com"
ping "server2.example.com"
ping "database.example.com"

# Download configuration files
try
download "https://config.example.com/settings.json" to settings.json
say "Configuration updated!"
catch
say "Using cached configuration"
end try
```

## File Extension

Crystal scripts use the `.cry` extension.

## License

Feel free to use and modify!
