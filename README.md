# NBA TL;DR
NBA TL;DR is a summary generator for NBA games, with the use of a fine-tuned LLaMA 2 7B model.

This project leverages official NBA game data via open source API client [nba_api](https://github.com/swar/nba_api), structures important game data with **pandas**, and uses **Unsloth**, **PyTorch**, and **Hugging Face** for efficient fine-tuning.

## Data Extraction and Formatting

The project uses [nba_api](https://github.com/swar/nba_api) to pull play-by-play logs, box scores, and game details. These are converted into structured DataFrames with **pandas**, then formatted into plain-text input for the model.

```text 
2025-04-26
First Round Game 3

Q1:
Miami Heat 20-33 Cleveland Cavaliers

Q2:
Miami Heat 22-29 Cleveland Cavaliers

Q3:
Miami Heat 22-26 Cleveland Cavaliers

Q4:
Miami Heat 23-36 Cleveland Cavaliers

FINAL:
Miami Heat 87-124 Cleveland Cavaliers
SERIES:
Miami Heat 0-3 Cleveland Cavaliers
LARGEST LEAD:
Miami Heat 9-40 Cleveland Cavaliers
LEAD CHANGES:
1
TIMES TIED: 
1
TOP PERFORMERS:
Name                 Team   Min    PTS    REB    AST   
----------------------------------------------------
Jarrett Allen        CLE    25     22     10     1     
Bam Adebayo          MIA    40     22     9      1     
De`Andre Hunter      CLE    28     21     4      3     
Evan Mobley          CLE    31     19     6      3     
Davion Mitchell      MIA    36     16     4      5     
Tyler Herro          MIA    36     13     4      3 
```

## Model Fine-Tuning
Game data is paired with a corresponding summary and added to a JSONL file for model fine-tuning.

```json
{
    "info": "2025-04-26\nFirst Round Game 3\n\nQ1:\nMiami Heat 20-33 Cleveland Cavaliers\n\nQ2:\nMiami Heat 22-29 Cleveland Cavaliers\n\nQ3:\nMiami Heat 22-26 Cleveland Cavaliers\n\nQ4:\nMiami Heat 23-36 Cleveland Cavaliers\n\nFINAL:\nMiami Heat 87-124 Cleveland Cavaliers\nSERIES:\nMiami Heat 0-3 Cleveland Cavaliers\nLARGEST LEAD:\nMiami Heat 9-40 Cleveland Cavaliers\nLEAD CHANGES:\n1\nTIMES TIED: \n1\nTOP PERFORMERS:\nName                 Team   Min    PTS    REB    AST   \n----------------------------------------------------\nJarrett Allen        CLE    25     22     10     1     \nBam Adebayo          MIA    40     22     9      1     \nDe`Andre Hunter      CLE    28     21     4      3     \nEvan Mobley          CLE    31     19     6      3     \nDavion Mitchell      MIA    36     16     4      5     \nTyler Herro          MIA    36     13     4      3", 
    "summary": "2025-04-26\nFirst Round Game 3\nCleveland Cavaliers 124-87 Miami Heat\n\nThe Cavaliers dominated Game 3 with a 124–87 win over the Heat, seizing a 3–0 series lead. Cleveland outscored Miami in every quarter and built a lead as large as 40 points, putting the game out of reach early and maintaining control throughout.\n\nJarrett Allen led Cleveland with 22 points and 10 rebounds in 25 minutes. De`Andre Hunter added 21 points and 3 assists, while Evan Mobley contributed 19 points and 6 boards. Bam Adebayo paced Miami with 22 points and 9 rebounds. Davion Mitchell finished with 16 points and 5 assists, and Tyler Herro scored 13.\n\nCleveland leads the series 3–0."
}
```

The LLaMA 2 7B model is fine-tuned using Unsloth, a wrapper around PyTorch and Hugging Face Transformers. This allows for more optimized, efficient training on a consumer GPU. Training is conducted using Hugging Face`s **Trainer API** with prompt-response pairs like the one above.

## Generated Samples
Summaries generated with the fine-tuned model
 
>2016-06-19
NBA Finals Game 7
Cleveland Cavaliers (93) vs (89) Golden State Warriors
>
> The Cavaliers and Warriors played a close and defensive Game 7, with both teams trading momentum throughout. The fourth quarter was especially tight, as neither side was able to build separation until Cleveland pulled ahead in the final minutes. The Cavaliers held on in the closing possessions to secure the win, outscoring the Warriors 18–13 in the fourth.
>
> LeBron James led Cleveland with 27 points, 11 rebounds, and 11 assists. Kyrie Irving added 26 points, including a key three-pointer late in the game, while Kevin Love contributed 9 rebounds and timely defense. For Golden State, Draymond Green posted 32 points, 15 rebounds, and 9 assists, while Stephen Curry finished with 17 points and 5 assists. Klay Thompson contributed 14 points, but the Warriors managed only 89 points in the loss.

> 1998-06-14
NBA Finals Game 6
Utah Jazz (86) vs (87) Chicago Bulls
>
> In a thrilling conclusion to the NBA Finals, the Chicago Bulls edged out the Utah Jazz 87-86 to claim the championship. Michael Jordan was the star of the game, finishing with 45 points and hitting the decisive shot with just 5.2 seconds left, a 17-foot jump shot to give the Bulls the lead for good.
>
> The game saw numerous lead changes and ties, with Utah holding a slight lead for most of the game. Karl Malone led the Jazz with 31 points and 11 rebounds, including a critical jump shot that gave Utah a brief 79-77 lead in the final minutes. John Stockton added 10 points, including a crucial 24-foot three-pointer that put Utah up 86-83. However, the Bulls were able to respond with clutch plays, including free throws from Dennis Rodman and Jordan, setting up Jordan's game-winning shot.
> 

## Future Work
- Add a larger number of diverse game examples to training dataset for higher quality summaries.
- Add automated evaluation metrics