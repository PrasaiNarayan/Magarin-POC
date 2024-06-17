from cx_Freeze import setup, Executable

# Add packages to 'packages' list
build_exe_options = {"packages": ["encodings", "encodings.shift_jis", "asyncio"]}

setup(
    name='ADEKA-POC',
    version='0.1',
    description='allocate manufacturing time of multiple lines',
    options={"build_exe": build_exe_options},  # Add this line
    executables=[Executable('outline_features.py')]
)
