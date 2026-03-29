import re

with open('ask.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Match the exact pattern
old_pattern = r"        \} catch \(e\) \{ console\.error\('AI error:', e\); \}\s+return \{ answer: \"That's a great question! We invite you to learn more by visiting the official Church website.\", sources: \[.\] \};"

replacement = """        } catch (e) { console.error('AI error:', e); }

        // Auto-retry once if first attempt fails
        try {
            const retryResp = await fetch('https://focuschrist-groq-proxy.caribousun.workers.dev', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: 'llama-3.1-8b-instant',
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 800
                })
            });
            const retryData = await retryResp.json();
            if (retryData.choices && retryData.choices[0]) {
                let ans = retryData.choices[0].message.content;
                ans = truncateToCompleteSentence(ans);
                return { answer: ans, sources: [] };
            }
        } catch(e) { console.error('AI retry error:', e); }

        return { answer: "That's a great question! We invite you to learn more by visiting the official Church website.", sources: [{text:'📜 Come Unto Christ',url:'https://www.churchofjesuschrist.org/comeuntochrist'}] };"""

# Try direct string replacement
search = "        } catch (e) { console.error('AI error:', e); }\n        return { answer: \"That"
replace = "        } catch (e) { console.error('AI error:', e); }\n\n        // Auto-retry once if first attempt fails\n        try {\n            const retryResp = await fetch('https://focuschrist-groq-proxy.caribousun.workers.dev', {\n                method: 'POST',\n                headers: { 'Content-Type': 'application/json' },\n                body: JSON.stringify({\n                    model: 'llama-3.1-8b-instant',\n                    messages: messages,\n                    temperature: 0.7,\n                    max_tokens: 800\n                })\n            });\n            const retryData = await retryResp.json();\n            if (retryData.choices && retryData.choices[0]) {\n                let ans = retryData.choices[0].message.content;\n                ans = truncateToCompleteSentence(ans);\n                return { answer: ans, sources: [] };\n            }\n        } catch(e) { console.error('AI retry error:', e); }\n\n        return { answer: \"That"

new_content = content.replace(search, replace)

if new_content == content:
    print("NOT FOUND")
else:
    with open('ask.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("DONE")