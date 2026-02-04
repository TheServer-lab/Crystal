#!/usr/bin/env python3
"""
Crystal - A simple, readable shell for Windows
"""

from lark import Lark, Transformer, v_args
import os
import sys

# Crystal Grammar Definition
CRYSTAL_GRAMMAR = r"""
    start: statement+

    statement: say_stmt
             | ask_stmt
             | set_stmt
             | if_stmt
             | repeat_stmt
             | copy_stmt
             | delete_stmt
             | move_stmt
             | list_stmt
             | create_stmt
             | make_stmt
             | include_stmt
             | function_def
             | function_call
             | pause_stmt
             | try_stmt
             | ping_stmt
             | download_stmt
             | path_stmt
             | cd_stmt
             | pwd_stmt
             | ls_stmt
             | zip_stmt
             | unzip_stmt
             | wait_stmt
             | error_stmt

    // Say command
    say_stmt: "say" STRING

    // Ask command
    ask_stmt: "ask" STRING ("local" | "global") VARIABLE

    // Set variable
    set_stmt: "set" ("local" | "global") VARIABLE "=" expression

    // If statement
    if_stmt: "if" condition NEWLINE statement+ ("otherwise" NEWLINE statement+)? "end" "if"

    // Repeat loops
    repeat_stmt: "repeat" repeat_type NEWLINE statement+ "end" "repeat"
    repeat_type: NUMBER                          -> repeat_count
               | "infinite"                      -> repeat_infinite
               | "while" condition               -> repeat_while
               | "until" condition               -> repeat_until
               | "for" "each" VARIABLE "in" file_path -> repeat_foreach

    // Copy command
    copy_stmt: "copy" file_path "to" file_path force?

    // Move command
    move_stmt: "move" file_path "to" file_path force?

    // Delete command
    delete_stmt: "delete" file_path force?

    // List files
    list_stmt: "list" ("files" | "folders" | "all")? ("in" file_path)?

    // Create file or folder
    create_stmt: "create" ("file" | "folder") file_path

    // Make file with content or folders (multiple)
    make_stmt: "make" "file" file_path STRING force?     -> make_file
             | "make" "folder" file_path+                 -> make_folders

    // Include other scripts
    include_stmt: "include" file_path

    // Function definition
    function_def: "function" NAME NEWLINE statement+ "end" "function"

    // Function call
    function_call: NAME

    // Pause execution
    pause_stmt: "pause" (STRING)?

    // Error handling
    try_stmt: "try" NEWLINE statement+ "catch" NEWLINE statement+ "end" "try"

    // Network operations
    ping_stmt: "ping" STRING
    download_stmt: "download" STRING "to" file_path force?

    // Path management
    path_stmt: "list" "path"                        -> list_path
             | "add" "path" file_path                     -> add_path
             | "remove" "path" file_path                  -> remove_path

    // Navigation commands
    cd_stmt: "cd" file_path
    pwd_stmt: "pwd"
    ls_stmt: "ls" file_path?

    // Zip operations
    zip_stmt: "zip" file_path+ "to" file_path
    unzip_stmt: "unzip" file_path "to" file_path

    // Wait/sleep command
    wait_stmt: "wait" NUMBER time_unit?
    time_unit: "second" | "seconds" | "minute" | "minutes" | "hour" | "hours"

    // Error command
    error_stmt: "error" STRING

    // Force flag
    force: "--force"

    // Conditions
    condition: file_exists
             | comparison

    file_exists: "{" file_path "}" "exists"
    
    comparison: expression COMP_OP expression
    COMP_OP: "greater" "than" | "less" "than" | "equals" | "is" | ">" | "<" | "="

    // Expressions and arithmetic
    expression: term
              | expression "+" term   -> add
              | expression "-" term   -> subtract
    
    term: factor
        | term "*" factor             -> multiply
        | term "/" factor             -> divide
        | term "%" factor             -> modulo
    
    factor: value
          | "(" expression ")"

    // Values
    value: STRING
         | NUMBER
         | VARIABLE
    
    file_path: PATH | STRING | VARIABLE
    
    // Tokens
    VARIABLE: "'" NAME "'"
    STRING: "\"" /[^"]*/ "\""
    PATH: /[A-Za-z]:[\/\\][^\s;]*/
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /[0-9]+/
    COMMENT: /#[^\n]*/

    // Whitespace
    %import common.WS
    %import common.NEWLINE
    %ignore WS
    %ignore COMMENT
"""


class CrystalInterpreter(Transformer):
    """Interprets and executes Crystal commands"""
    
    def __init__(self):
        self.local_vars = {}
        self.global_vars = self.load_global_vars()
        self.functions = {}  # Store user-defined functions
        self.current_dir = os.getcwd()  # Track current directory
    
    def load_global_vars(self):
        """Load global variables from file (if exists)"""
        # TODO: Implement persistent storage
        return {}
    
    def save_global_vars(self):
        """Save global variables to file"""
        # TODO: Implement persistent storage
        pass
    
    # Statements
    def say_stmt(self, args):
        """Execute say command"""
        text = args[0] if isinstance(args, list) else args
        message = self.resolve_value(text)
        print(message)
    
    def ask_stmt(self, args):
        """Execute ask command"""
        prompt, scope, var_name = args[0], args[1], args[2]
        prompt_text = self.resolve_value(prompt)
        user_input = input(prompt_text + " ")
        
        var = str(var_name).strip("'")
        if str(scope) == "local":
            self.local_vars[var] = user_input
        else:
            self.global_vars[var] = user_input
            self.save_global_vars()
    
    def set_stmt(self, args):
        """Execute set command"""
        scope, var_name, expr = args[0], args[1], args[2]
        var = str(var_name).strip("'")
        value = self.evaluate_expression(expr)
        
        if str(scope) == "local":
            self.local_vars[var] = value
        else:
            self.global_vars[var] = value
            self.save_global_vars()
    
    # Arithmetic operations
    def evaluate_expression(self, expr):
        """Evaluate an arithmetic expression"""
        if hasattr(expr, 'data'):
            if expr.data == 'add':
                left = self.evaluate_expression(expr.children[0])
                right = self.evaluate_expression(expr.children[1])
                return self.to_number(left) + self.to_number(right)
            
            elif expr.data == 'subtract':
                left = self.evaluate_expression(expr.children[0])
                right = self.evaluate_expression(expr.children[1])
                return self.to_number(left) - self.to_number(right)
            
            elif expr.data == 'multiply':
                left = self.evaluate_expression(expr.children[0])
                right = self.evaluate_expression(expr.children[1])
                return self.to_number(left) * self.to_number(right)
            
            elif expr.data == 'divide':
                left = self.evaluate_expression(expr.children[0])
                right = self.evaluate_expression(expr.children[1])
                divisor = self.to_number(right)
                if divisor == 0:
                    print("[ERROR] Division by zero")
                    return 0
                return self.to_number(left) / divisor
            
            elif expr.data == 'modulo':
                left = self.evaluate_expression(expr.children[0])
                right = self.evaluate_expression(expr.children[1])
                return self.to_number(left) % self.to_number(right)
            
            elif expr.data == 'expression' or expr.data == 'term' or expr.data == 'factor':
                # Unwrap nested expression nodes
                return self.evaluate_expression(expr.children[0])
        
        # Base case: it's a value
        return self.resolve_value(expr)
    
    def to_number(self, value):
        """Convert a value to a number"""
        try:
            # Try integer first
            if isinstance(value, (int, float)):
                return value
            
            # Try parsing as float
            val_str = str(value)
            if '.' in val_str:
                return float(val_str)
            else:
                return int(val_str)
        except ValueError:
            print(f"[ERROR] Cannot convert '{value}' to number")
            return 0
    
    def if_stmt(self, args):
        """Execute if statement"""
        condition = args[0]
        
        # Find where 'otherwise' starts (if it exists)
        otherwise_index = None
        for i, arg in enumerate(args[1:], 1):
            if hasattr(arg, 'type') and str(arg) == 'otherwise':
                otherwise_index = i
                break
        
        if otherwise_index:
            if_statements = args[1:otherwise_index]
            else_statements = args[otherwise_index+1:]
        else:
            if_statements = args[1:]
            else_statements = []
        
        if self.evaluate_condition(condition):
            for stmt in if_statements:
                self.execute_statement(stmt)
        elif else_statements:
            for stmt in else_statements:
                self.execute_statement(stmt)
    
    def repeat_stmt(self, args):
        """Execute repeat loop"""
        repeat_type = args[0]
        statements = args[1:]
        
        # Get the type of repeat
        type_name = repeat_type.data if hasattr(repeat_type, 'data') else None
        
        if type_name == 'repeat_infinite':
            # Infinite loop
            try:
                while True:
                    for stmt in statements:
                        self.execute_statement(stmt)
            except KeyboardInterrupt:
                print("\n[Loop interrupted]")
        
        elif type_name == 'repeat_count':
            # Repeat N times
            count = int(self.resolve_value(repeat_type.children[0]))
            for _ in range(count):
                for stmt in statements:
                    self.execute_statement(stmt)
        
        elif type_name == 'repeat_while':
            # Repeat while condition is true
            condition = repeat_type.children[0]
            while self.evaluate_condition(condition):
                for stmt in statements:
                    self.execute_statement(stmt)
        
        elif type_name == 'repeat_until':
            # Repeat until condition is true
            condition = repeat_type.children[0]
            while not self.evaluate_condition(condition):
                for stmt in statements:
                    self.execute_statement(stmt)
        
        elif type_name == 'repeat_foreach':
            # For each item in collection
            var_name = str(repeat_type.children[0]).strip("'")
            path = self.resolve_value(repeat_type.children[1])
            
            # Get files in directory
            if os.path.isdir(path):
                items = os.listdir(path)
                for item in items:
                    self.local_vars[var_name] = item
                    for stmt in statements:
                        self.execute_statement(stmt)
            else:
                print(f"[ERROR] Not a directory: {path}")
    
    def copy_stmt(self, args):
        """Execute copy command"""
        import shutil
        
        # Check for --force flag
        force = False
        if args and str(args[-1]) == '--force':
            force = True
            args = args[:-1]
        
        source, dest = args[0], args[1]
        src = self.resolve_value(source)
        dst = self.resolve_value(dest)
        
        # Handle relative paths
        if not os.path.isabs(src):
            src = os.path.join(self.current_dir, src)
        if not os.path.isabs(dst):
            dst = os.path.join(self.current_dir, dst)
        
        # Check if source exists
        if not os.path.exists(src):
            print(f"[ERROR] Source not found: {src}")
            return
        
        # Check if destination already exists
        if os.path.exists(dst) and not force:
            confirm = input(f"'{dst}' already exists. Overwrite? (yes/no) ")
            if confirm.lower() not in ['yes', 'y']:
                print("[CANCELLED] Copy operation cancelled")
                return
        
        try:
            # Copy file or directory
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"[SUCCESS] Copied file: {src} -> {dst}")
            elif os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"[SUCCESS] Copied directory: {src} -> {dst}")
        except Exception as e:
            print(f"[ERROR] Failed to copy: {e}")
    
    def move_stmt(self, args):
        """Execute move command"""
        import shutil
        
        # Check for --force flag
        force = False
        if args and str(args[-1]) == '--force':
            force = True
            args = args[:-1]
        
        source, dest = args[0], args[1]
        src = self.resolve_value(source)
        dst = self.resolve_value(dest)
        
        # Handle relative paths
        if not os.path.isabs(src):
            src = os.path.join(self.current_dir, src)
        if not os.path.isabs(dst):
            dst = os.path.join(self.current_dir, dst)
        
        # Check if source exists
        if not os.path.exists(src):
            print(f"[ERROR] Source not found: {src}")
            return
        
        # Check if destination already exists
        if os.path.exists(dst) and not force:
            confirm = input(f"'{dst}' already exists. Overwrite? (yes/no) ")
            if confirm.lower() not in ['yes', 'y']:
                print("[CANCELLED] Move operation cancelled")
                return
        
        try:
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            shutil.move(src, dst)
            print(f"[SUCCESS] Moved: {src} -> {dst}")
        except Exception as e:
            print(f"[ERROR] Failed to move: {e}")
    
    def delete_stmt(self, args):
        """Execute delete command"""
        import shutil
        
        # Check for --force flag
        force = False
        if args and str(args[-1]) == '--force':
            force = True
            args = args[:-1]
        
        target = args[0] if isinstance(args, list) else args
        path = self.resolve_value(target)
        
        # Handle relative paths
        if not os.path.isabs(path):
            path = os.path.join(self.current_dir, path)
        
        # Check if path exists
        if not os.path.exists(path):
            print(f"[ERROR] Path not found: {path}")
            return
        
        # Get file/directory info
        if os.path.isfile(path):
            item_type = "file"
            size = os.path.getsize(path)
        elif os.path.isdir(path):
            item_type = "directory"
            # Count files in directory
            file_count = sum(len(files) for _, _, files in os.walk(path))
            size = f"{file_count} files"
        else:
            item_type = "item"
            size = "unknown"
        
        # Confirm deletion
        if not force:
            print(f"[WARNING] About to delete {item_type}: {path}")
            if item_type == "directory":
                print(f"          Contains: {size}")
            confirm = input("Are you sure? (yes/no) ")
            
            if confirm.lower() not in ['yes', 'y']:
                print("[CANCELLED] Delete operation cancelled")
                return
        
        try:
            # Delete file or directory
            if os.path.isfile(path):
                os.remove(path)
                print(f"[SUCCESS] Deleted file: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                print(f"[SUCCESS] Deleted directory: {path}")
        except Exception as e:
            print(f"[ERROR] Failed to delete: {e}")
    
    def list_stmt(self, args):
        """Execute list command"""
        # Parse arguments
        filter_type = "all"  # default
        target_path = "."    # current directory
        
        for arg in args:
            arg_str = str(arg)
            if arg_str in ["files", "folders", "all"]:
                filter_type = arg_str
            else:
                target_path = self.resolve_value(arg)
        
        # Check if path exists
        if not os.path.exists(target_path):
            print(f"[ERROR] Path not found: {target_path}")
            return
        
        if not os.path.isdir(target_path):
            print(f"[ERROR] Not a directory: {target_path}")
            return
        
        try:
            items = os.listdir(target_path)
            
            # Filter items
            filtered_items = []
            for item in items:
                full_path = os.path.join(target_path, item)
                if filter_type == "files" and os.path.isfile(full_path):
                    filtered_items.append(item)
                elif filter_type == "folders" and os.path.isdir(full_path):
                    filtered_items.append(item + "/")
                elif filter_type == "all":
                    if os.path.isdir(full_path):
                        filtered_items.append(item + "/")
                    else:
                        filtered_items.append(item)
            
            # Display results
            if filtered_items:
                print(f"\nListing {filter_type} in: {target_path}")
                print("-" * 50)
                for item in sorted(filtered_items):
                    print(f"  {item}")
                print(f"\nTotal: {len(filtered_items)} item(s)")
            else:
                print(f"No {filter_type} found in: {target_path}")
        
        except Exception as e:
            print(f"[ERROR] Failed to list directory: {e}")
    
    def create_stmt(self, args):
        """Execute create command"""
        item_type = str(args[0])
        target_path = self.resolve_value(args[1])
        
        # Check if already exists
        if os.path.exists(target_path):
            print(f"[ERROR] Already exists: {target_path}")
            return
        
        try:
            if item_type == "file":
                # Create empty file
                with open(target_path, 'w') as f:
                    pass
                print(f"[SUCCESS] Created file: {target_path}")
            
            elif item_type == "folder":
                # Create directory
                os.makedirs(target_path, exist_ok=True)
                print(f"[SUCCESS] Created folder: {target_path}")
        
        except Exception as e:
            print(f"[ERROR] Failed to create {item_type}: {e}")
    
    def pause_stmt(self, args):
        """Execute pause command"""
        # Check if a custom message was provided
        if args and len(args) > 0:
            message = self.resolve_value(args[0])
        else:
            message = "Press Enter to continue..."
        
        input(message)
    
    def make_file(self, args):
        """Make a file with content"""
        # Check for --force flag
        force = False
        if args and str(args[-1]) == '--force':
            force = True
            args = args[:-1]
        
        target_path = self.resolve_value(args[0])
        content = self.resolve_value(args[1])
        
        # Handle relative paths
        if not os.path.isabs(target_path):
            target_path = os.path.join(self.current_dir, target_path)
        
        # Check if already exists
        if os.path.exists(target_path) and not force:
            confirm = input(f"'{target_path}' already exists. Overwrite? (yes/no) ")
            if confirm.lower() not in ['yes', 'y']:
                print("[CANCELLED] Make file operation cancelled")
                return
        
        try:
            # Create any necessary parent directories
            parent_dir = os.path.dirname(target_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write content to file
            with open(target_path, 'w') as f:
                f.write(content)
            print(f"[SUCCESS] Created file: {target_path}")
        
        except Exception as e:
            print(f"[ERROR] Failed to create file: {e}")
    
    def make_folders(self, args):
        """Make one or more folders (creates full path)"""
        created_folders = []
        
        for path_arg in args:
            target_path = self.resolve_value(path_arg)
            
            # Handle relative paths
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_dir, target_path)
            
            try:
                # Create directory and all parent directories
                os.makedirs(target_path, exist_ok=True)
                created_folders.append(target_path)
            
            except Exception as e:
                print(f"[ERROR] Failed to create folder '{target_path}': {e}")
        
        if created_folders:
            print(f"[SUCCESS] Created {len(created_folders)} folder(s):")
            for folder in created_folders:
                print(f"  - {folder}")
    
    def include_stmt(self, args):
        """Include another Crystal script"""
        script_path = self.resolve_value(args[0])
        
        # Check if file exists
        if not os.path.exists(script_path):
            print(f"[ERROR] Script not found: {script_path}")
            return
        
        try:
            # Read the script file
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            # Parse and execute the included script
            from lark import Lark
            parser = Lark(CRYSTAL_GRAMMAR, start='start', parser='lalr')
            tree = parser.parse(script_content + "\n")
            
            # Execute in the current interpreter context
            # This allows sharing variables and functions
            for stmt in tree.children:
                self.execute_statement(stmt)
            
            print(f"[INCLUDED] {script_path}")
        
        except Exception as e:
            print(f"[ERROR] Failed to include script: {e}")
    
    def function_def(self, args):
        """Define a function"""
        # Get function name
        func_name = str(args[0])
        
        # Store the function body (all statements except the name)
        func_body = args[1:]
        
        self.functions[func_name] = func_body
        print(f"[FUNCTION] Defined: {func_name}")
    
    def function_call(self, args):
        """Call a user-defined function"""
        func_name = str(args[0]) if args else None
        
        if not func_name:
            return
        
        # Check if function exists
        if func_name not in self.functions:
            # Not a function, might be a path or unknown command
            return
        
        # Execute function body
        func_body = self.functions[func_name]
        for stmt in func_body:
            self.execute_statement(stmt)
    
    def try_stmt(self, args):
        """Execute try-catch block"""
        # Split into try and catch statements
        # Find where catch starts
        try_statements = []
        catch_statements = []
        in_catch = False
        
        for stmt in args:
            if hasattr(stmt, 'type') and str(stmt) == 'catch':
                in_catch = True
                continue
            
            if in_catch:
                catch_statements.append(stmt)
            else:
                try_statements.append(stmt)
        
        # Execute try block
        try:
            for stmt in try_statements:
                self.execute_statement(stmt)
        except Exception as e:
            # Execute catch block on error
            print(f"[ERROR CAUGHT] {e}")
            for stmt in catch_statements:
                self.execute_statement(stmt)
    
    def ping_stmt(self, args):
        """Ping a host"""
        import subprocess
        import platform
        
        target = self.resolve_value(args[0])
        
        # Get ping command based on OS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '4', target]
        
        try:
            print(f"Pinging {target}...")
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            
            # Show output
            print(result.stdout)
            
            if result.returncode == 0:
                print(f"[SUCCESS] {target} is reachable")
            else:
                print(f"[FAILED] {target} is unreachable")
        
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] Ping to {target} timed out")
        except Exception as e:
            print(f"[ERROR] Failed to ping: {e}")
    
    def download_stmt(self, args):
        """Download a file from URL"""
        # Check for --force flag
        force = False
        if args and str(args[-1]) == '--force':
            force = True
            args = args[:-1]
        
        url = self.resolve_value(args[0])
        dest = self.resolve_value(args[1])
        
        # Handle relative paths
        if not os.path.isabs(dest):
            dest = os.path.join(self.current_dir, dest)
        
        try:
            import urllib.request
            
            print(f"Downloading {url}...")
            
            # Check if destination exists
            if os.path.exists(dest) and not force:
                confirm = input(f"'{dest}' already exists. Overwrite? (yes/no) ")
                if confirm.lower() not in ['yes', 'y']:
                    print("[CANCELLED] Download cancelled")
                    return
            
            # Create parent directories if needed
            parent_dir = os.path.dirname(dest)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            # Download file
            urllib.request.urlretrieve(url, dest)
            
            # Get file size
            size = os.path.getsize(dest)
            size_kb = size / 1024
            
            print(f"[SUCCESS] Downloaded to {dest} ({size_kb:.2f} KB)")
        
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
    
    # Path management commands
    def list_path(self, args):
        """List PATH environment variable"""
        path_var = os.environ.get('PATH', '')
        paths = path_var.split(os.pathsep)
        
        print("PATH entries:")
        print("=" * 60)
        for i, p in enumerate(paths, 1):
            print(f"{i}. {p}")
        print(f"\nTotal: {len(paths)} entries")
    
    def add_path(self, args):
        """Add directory to PATH"""
        new_path = self.resolve_value(args[0])
        
        # Handle relative paths
        if not os.path.isabs(new_path):
            new_path = os.path.join(self.current_dir, new_path)
        
        if not os.path.exists(new_path):
            print(f"[WARNING] Path does not exist: {new_path}")
        
        current_path = os.environ.get('PATH', '')
        if new_path in current_path:
            print(f"[INFO] Path already in PATH: {new_path}")
            return
        
        os.environ['PATH'] = new_path + os.pathsep + current_path
        print(f"[SUCCESS] Added to PATH: {new_path}")
        print("[NOTE] This change is only for the current session")
    
    def remove_path(self, args):
        """Remove directory from PATH"""
        target_path = self.resolve_value(args[0])
        
        # Handle relative paths
        if not os.path.isabs(target_path):
            target_path = os.path.join(self.current_dir, target_path)
        
        current_path = os.environ.get('PATH', '')
        paths = current_path.split(os.pathsep)
        
        if target_path not in paths:
            print(f"[INFO] Path not in PATH: {target_path}")
            return
        
        paths.remove(target_path)
        os.environ['PATH'] = os.pathsep.join(paths)
        print(f"[SUCCESS] Removed from PATH: {target_path}")
        print("[NOTE] This change is only for the current session")
    
    # Navigation commands
    def cd_stmt(self, args):
        """Change current directory"""
        target = self.resolve_value(args[0])
        
        # Handle relative paths
        if not os.path.isabs(target):
            target = os.path.join(self.current_dir, target)
        
        # Resolve path (handle .. and .)
        target = os.path.abspath(target)
        
        if not os.path.exists(target):
            print(f"[ERROR] Directory not found: {target}")
            return
        
        if not os.path.isdir(target):
            print(f"[ERROR] Not a directory: {target}")
            return
        
        self.current_dir = target
        os.chdir(target)
        print(f"[CD] {target}")
    
    def pwd_stmt(self, args):
        """Print working directory"""
        print(self.current_dir)
    
    def ls_stmt(self, args):
        """List files in directory (alias for list)"""
        target_path = "."
        
        if args and len(args) > 0:
            target_path = self.resolve_value(args[0])
        
        # Handle relative paths
        if not os.path.isabs(target_path):
            target_path = os.path.join(self.current_dir, target_path)
        
        if not os.path.exists(target_path):
            print(f"[ERROR] Path not found: {target_path}")
            return
        
        if not os.path.isdir(target_path):
            print(f"[ERROR] Not a directory: {target_path}")
            return
        
        try:
            items = os.listdir(target_path)
            
            # Separate files and folders
            files = []
            folders = []
            
            for item in items:
                full_path = os.path.join(target_path, item)
                if os.path.isdir(full_path):
                    folders.append(item)
                else:
                    files.append(item)
            
            print(f"\n{target_path}")
            print("=" * 60)
            
            # Show folders first
            if folders:
                for folder in sorted(folders):
                    print(f"  [DIR]  {folder}")
            
            if files:
                for file in sorted(files):
                    full_path = os.path.join(target_path, file)
                    size = os.path.getsize(full_path)
                    size_str = f"{size:,}" if size < 1024 else f"{size/1024:.1f}K"
                    print(f"  {size_str:>8}  {file}")
            
            print(f"\n{len(folders)} folder(s), {len(files)} file(s)")
        
        except Exception as e:
            print(f"[ERROR] Failed to list directory: {e}")
    
    # Zip operations
    def zip_stmt(self, args):
        """Zip files into an archive"""
        import zipfile
        
        # Last arg is destination, rest are source files
        dest_zip = self.resolve_value(args[-1])
        source_files = args[:-1]
        
        # Handle relative paths
        if not os.path.isabs(dest_zip):
            dest_zip = os.path.join(self.current_dir, dest_zip)
        
        # Ensure .zip extension
        if not dest_zip.endswith('.zip'):
            dest_zip += '.zip'
        
        try:
            with zipfile.ZipFile(dest_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for source_arg in source_files:
                    source = self.resolve_value(source_arg)
                    
                    # Handle relative paths
                    if not os.path.isabs(source):
                        source = os.path.join(self.current_dir, source)
                    
                    if not os.path.exists(source):
                        print(f"[WARNING] Skipping (not found): {source}")
                        continue
                    
                    if os.path.isfile(source):
                        zipf.write(source, os.path.basename(source))
                        print(f"  Added: {source}")
                    elif os.path.isdir(source):
                        # Add directory recursively
                        for root, dirs, files in os.walk(source):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.dirname(source))
                                zipf.write(file_path, arcname)
                                print(f"  Added: {file_path}")
            
            size = os.path.getsize(dest_zip)
            size_kb = size / 1024
            print(f"[SUCCESS] Created zip: {dest_zip} ({size_kb:.2f} KB)")
        
        except Exception as e:
            print(f"[ERROR] Failed to create zip: {e}")
    
    def unzip_stmt(self, args):
        """Unzip an archive"""
        import zipfile
        
        source_zip = self.resolve_value(args[0])
        dest_dir = self.resolve_value(args[1])
        
        # Handle relative paths
        if not os.path.isabs(source_zip):
            source_zip = os.path.join(self.current_dir, source_zip)
        if not os.path.isabs(dest_dir):
            dest_dir = os.path.join(self.current_dir, dest_dir)
        
        if not os.path.exists(source_zip):
            print(f"[ERROR] Zip file not found: {source_zip}")
            return
        
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(dest_dir, exist_ok=True)
            
            with zipfile.ZipFile(source_zip, 'r') as zipf:
                zipf.extractall(dest_dir)
                file_count = len(zipf.namelist())
            
            print(f"[SUCCESS] Extracted {file_count} file(s) to: {dest_dir}")
        
        except Exception as e:
            print(f"[ERROR] Failed to unzip: {e}")
    
    def wait_stmt(self, args):
        """Wait/sleep for a specified duration"""
        import time
        
        # Get the number
        amount = int(self.resolve_value(args[0]))
        
        # Get the time unit (default to seconds)
        unit = "seconds"
        if len(args) > 1:
            unit = str(args[1]).lower()
        
        # Calculate sleep time in seconds
        if unit in ['second', 'seconds']:
            sleep_time = amount
        elif unit in ['minute', 'minutes']:
            sleep_time = amount * 60
        elif unit in ['hour', 'hours']:
            sleep_time = amount * 3600
        else:
            sleep_time = amount  # Default to seconds
        
        # Display what we're doing
        if sleep_time < 60:
            print(f"[WAIT] Waiting {amount} second(s)...")
        elif sleep_time < 3600:
            print(f"[WAIT] Waiting {amount} minute(s)...")
        else:
            print(f"[WAIT] Waiting {amount} hour(s)...")
        
        # Sleep
        time.sleep(sleep_time)
        print("[WAIT] Done!")
    
    def error_stmt(self, args):
        """Raise a custom error"""
        message = self.resolve_value(args[0])
        raise Exception(message)
    
    def chain_stmt(self, args):
        """Execute chained commands"""
        for stmt in args:
            self.execute_statement(stmt)
    
    # Condition evaluation
    def evaluate_condition(self, condition):
        """Evaluate a condition and return boolean"""
        if hasattr(condition, 'data'):
            if condition.data == 'file_exists':
                # Check if file exists
                path = self.resolve_value(condition.children[0])
                return os.path.exists(path)
            
            elif condition.data == 'comparison':
                # Compare two values
                left = self.evaluate_expression(condition.children[0])
                op = str(condition.children[1])
                right = self.evaluate_expression(condition.children[2])
                
                # Try to convert to numbers if possible for numeric comparison
                try:
                    left_num = self.to_number(left)
                    right_num = self.to_number(right)
                    
                    if op in ['greater than', '>']:
                        return left_num > right_num
                    elif op in ['less than', '<']:
                        return left_num < right_num
                    elif op in ['equals', 'is', '=']:
                        return left_num == right_num
                except:
                    # Fall back to string comparison
                    if op in ['equals', 'is', '=']:
                        return str(left) == str(right)
                    else:
                        print(f"[ERROR] Cannot compare non-numeric values with {op}")
                        return False
                
        return False
    
    def execute_statement(self, stmt):
        """Execute a single statement"""
        if hasattr(stmt, 'data'):
            stmt_type = stmt.data
            
            if stmt_type == 'say_stmt':
                self.say_stmt(stmt.children)
            elif stmt_type == 'ask_stmt':
                self.ask_stmt(stmt.children)
            elif stmt_type == 'set_stmt':
                self.set_stmt(stmt.children)
            elif stmt_type == 'if_stmt':
                self.if_stmt(stmt.children)
            elif stmt_type == 'repeat_stmt':
                self.repeat_stmt(stmt.children)
            elif stmt_type == 'copy_stmt':
                self.copy_stmt(stmt.children)
            elif stmt_type == 'move_stmt':
                self.move_stmt(stmt.children)
            elif stmt_type == 'delete_stmt':
                self.delete_stmt(stmt.children)
            elif stmt_type == 'list_stmt':
                self.list_stmt(stmt.children)
            elif stmt_type == 'create_stmt':
                self.create_stmt(stmt.children)
            elif stmt_type == 'make_file':
                self.make_file(stmt.children)
            elif stmt_type == 'make_folders':
                self.make_folders(stmt.children)
            elif stmt_type == 'include_stmt':
                self.include_stmt(stmt.children)
            elif stmt_type == 'function_def':
                self.function_def(stmt.children)
            elif stmt_type == 'function_call':
                self.function_call(stmt.children)
            elif stmt_type == 'pause_stmt':
                self.pause_stmt(stmt.children)
            elif stmt_type == 'try_stmt':
                self.try_stmt(stmt.children)
            elif stmt_type == 'ping_stmt':
                self.ping_stmt(stmt.children)
            elif stmt_type == 'download_stmt':
                self.download_stmt(stmt.children)
            elif stmt_type == 'list_path':
                self.list_path(stmt.children)
            elif stmt_type == 'add_path':
                self.add_path(stmt.children)
            elif stmt_type == 'remove_path':
                self.remove_path(stmt.children)
            elif stmt_type == 'cd_stmt':
                self.cd_stmt(stmt.children)
            elif stmt_type == 'pwd_stmt':
                self.pwd_stmt(stmt.children)
            elif stmt_type == 'ls_stmt':
                self.ls_stmt(stmt.children)
            elif stmt_type == 'zip_stmt':
                self.zip_stmt(stmt.children)
            elif stmt_type == 'unzip_stmt':
                self.unzip_stmt(stmt.children)
            elif stmt_type == 'wait_stmt':
                self.wait_stmt(stmt.children)
            elif stmt_type == 'error_stmt':
                self.error_stmt(stmt.children)
    
    # Values and resolution
    def resolve_value(self, val):
        """Resolve a value (handle variables, strings, numbers)"""
        # Handle Tree objects
        if hasattr(val, 'data') and val.data == 'value':
            val = val.children[0]
        
        if hasattr(val, 'data') and val.data == 'path':
            val = val.children[0]
        
        # Handle Token objects
        if hasattr(val, 'type'):
            val = str(val.value)
        
        val_str = str(val)
        
        # Variable reference
        if val_str.startswith("'") and val_str.endswith("'"):
            var_name = val_str.strip("'")
            if var_name in self.local_vars:
                return self.local_vars[var_name]
            elif var_name in self.global_vars:
                return self.global_vars[var_name]
            else:
                return f"[UNDEFINED: {var_name}]"
        
        # String literal
        if val_str.startswith('"') and val_str.endswith('"'):
            # Handle variable substitution in strings
            text = val_str.strip('"')
            # Replace 'varname' with actual values
            for var, value in {**self.global_vars, **self.local_vars}.items():
                text = text.replace(f"'{var}'", str(value))
            return text
        
        # Number or path
        return val_str
    
    # Tree transformation methods
    def start(self, statements):
        """Execute all statements"""
        for stmt in statements:
            self.execute_statement(stmt)
        return None


def main():
    """Main REPL loop"""
    parser = Lark(CRYSTAL_GRAMMAR, start='start', parser='lalr')
    interpreter = CrystalInterpreter()
    
    # Check if a script file was provided
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
        
        # Check if file exists
        if not os.path.exists(script_file):
            print(f"Error: Script file not found: {script_file}")
            sys.exit(1)
        
        # Check if it's a .cry file
        if not script_file.endswith('.cry'):
            print(f"Warning: '{script_file}' is not a .cry file")
        
        # Read and execute the script
        try:
            with open(script_file, 'r') as f:
                script_content = f.read()
            
            print(f"Running Crystal script: {script_file}\n")
            tree = parser.parse(script_content + "\n")
            interpreter.transform(tree)
            
        except Exception as e:
            print(f"Error executing script: {e}")
            sys.exit(1)
        
        return
    
    # Interactive REPL mode
    print("Crystal Shell v0.1")
    print("Type 'exit' to quit")
    print("Run a script: crystal script.cry\n")
    
    while True:
        try:
            # Read input
            line = input("crystal> ")
            
            if line.strip().lower() == 'exit':
                break
            
            if not line.strip():
                continue
            
            # Parse and execute
            tree = parser.parse(line + "\n")
            interpreter.transform(tree)
            
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
