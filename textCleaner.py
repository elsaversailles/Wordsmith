import re
import sys

def remove_extra_spaces(text_file, new_file, flags):
  """
  Dataset text cleaner
  
  Removes all extra spaces from a text file, removes text and symbols encapsulated in brackets, removes "Edit" text, and makes it single line.

  Args:
    text_file: The path to the text file.
    new_file: The path to the new file.
    flags: A string of cleaning operations to be performed.

  Returns:
    The text file with all extra spaces removed, text and symbols encapsulated in brackets removed, "Edit" text removed, and made single line.
  """

  with open(text_file, "r") as f:
    text = f.read()

  text = text.replace("  ", " ")
  text = text.replace("\n\n", "\n")

  if "-a" in flags:
    flags = ["-1", "-2", "-3", "-4"]

  if isinstance(flags, list):
    flags = ' '.join(flags)

  for flag in flags.split(" "):
    if flag == "-1":
      pattern = re.compile(r"\[[^\]]+\]")
      text = pattern.sub("", text)

    if flag == "-2":
      text = text.replace("\n", "")

    if flag == "-3":
      text = text.replace("Edit", "")

    if flag == "-4":
      text = text.replace("-", "")

  with open(new_file, "w") as f:
    f.write(text)


def main():
  text_file = input("\nEnter path and name to the text file: \n" )
  new_file = input("\nEnter path and name to the new file: \n")

  flags = input("\nEnter a cleaning args (-a to apply all cleaning options, -1 to remove text inside brackets, -2 to remove all spaces, -3 to make text single line, -4 to remove Edit text, and press SPACE to seperate args and ENTER to run): \n \n")

  flags = str(flags.strip())

  remove_extra_spaces(text_file, new_file, flags)


if __name__ == "__main__":
  main()
