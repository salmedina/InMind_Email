# Server I/O design

The request and response is going to be through a RESTful service using JSON as the potrayer.

## Input

- subject
- body
- sender
- user_name

## Output

- scheduling: bool
- entitites:
  - what: str
  - where: str
  - when: str (standart DT format)
  - who: str[]





---

```
def  solve_email_corref(text, i_replacement, you_replacemnt):

	# Tokenize
	# Find [i, you]
	# POS TAG
		# If found [i, you] are pronouns
			# replace
    # return

def preprocess_email(text, i_replacement, you_replacemnt):

	processed_text = solve_email_corref(text, i_replacement, you_replacemnt)

	return processed_text
```





