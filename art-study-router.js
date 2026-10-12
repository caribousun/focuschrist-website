/* focusChrist Art -> topic study / official Church search / contextual Ask router.
 * Preserves artwork unchanged. Study connections appear only in the open modal.
 * Production hardening: no generic YouTube study exit; Ask carries artwork context and an exact return path.
 */
(function () {
    'use strict';

    const CHURCH_SEARCH = 'https://www.churchofjesuschrist.org/search?lang=eng&query=';

    const TITLE_ALIASES = {
    "Jesus Boat": "Jesus with His Disciples at Sea",
    "Jesus Fun": "Joy Beside the Lake",
    "Jesus Leper": "The Healing Touch of Jesus",
    "Jesus Seven Times Seven": "Learning to Forgive",
    "Jesus with Apostles Sunflowers": "Walking with the Apostles",
    "Jesus and Mary His Mom": "Jesus and His Mother Mary",
    "Widows Mite": "The Widow's Mite"
};

    const PICTURE_STORIES = {
    "Divine Push": {
        "paragraphs": [
            "The woman keeps her hands on the handcart while two children rest inside. Behind her, Christ bends to help move its weight over the rocky ground. The long trail remains, but the effort is shared. In this tender picture of pioneer endurance, His help is close enough to touch the very burden she carries.",
            "Mosiah 24:14–15 tells how the Lord strengthened Alma's people to bear their burdens before their deliverance came. That promise gives the scene its spiritual meaning. Sometimes help arrives as renewed strength, a willing neighbor, or enough courage for the next step. The children can rest while the adults keep going; care itself becomes part of the journey."
        ],
        "sources": [
            {
                "label": "Mosiah 24:14–15",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah/24?lang=eng&id=p14-p15#p14"
            }
        ]
    },
    "Forever Friends": {
        "paragraphs": [
            "A forest path, an easy smile, and a hand resting on a shoulder make this meeting feel wonderfully familiar. The man's blue suit brings the scene into everyday life. Christ walks beside him as a companion, and their shared smile gives friendship a place in the picture of discipleship.",
            "In John 15:12–15, Jesus asks His disciples to love one another and calls them His friends. His friendship includes truth, sacrifice, and a life shaped by love. The warmth here invites us to think of prayer as honest conversation and of following Him as a relationship that can deepen through ordinary days, as well as difficult ones."
        ],
        "sources": [
            {
                "label": "John 15:12–15",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/15?lang=eng&id=p12-p15#p12"
            }
        ]
    },
    "Forever": {
        "paragraphs": [
            "Christ kneels between two grieving people beside a grave marked Forever. He is down at their level, holding them close. The sunset reaches across the cemetery, but the sorrow has not been hurried away. The picture gives quiet space to both love and loss.",
            "At Lazarus's death, Jesus wept with those who mourned, even as He testified of resurrection. John 11:25–35 holds those truths together: hope in Him and tears belong in the same story. For someone missing a loved one, this embrace can be a reminder that grief need not be faced alone and that Christ's promise reaches beyond the grave."
        ],
        "sources": [
            {
                "label": "John 11:25–35",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/11?lang=eng&id=p25-p35#p25"
            }
        ]
    },
    "Jesus and His Mother Mary": {
        "paragraphs": [
            "Mary leans into her Son's embrace beneath the olive trees. Their smiles give the scene the warmth of a family bond, with years of care suggested by the closeness of their faces and hands. Here the Savior who blesses multitudes also has time for His mother.",
            "John 19:25–27 records His concern for Mary even from the cross, when He entrusted her to the beloved disciple's care. The peaceful embrace gives us a moment to linger over that enduring love. Honoring those who have cared for us can be a deeply practical part of following Christ: making time, listening carefully, and offering affection while we can."
        ],
        "sources": [
            {
                "label": "John 19:25–27",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/19?lang=eng&id=p25-p27#p25"
            }
        ]
    },
    "Jesus Baptized": {
        "paragraphs": [
            "John stands with Jesus in the river as people watch from the bank and a white dove appears above. The water and the attentive figures draw us toward a quiet act of obedience at the beginning of the Savior's ministry.",
            "Matthew 3:13–17 tells of Jesus coming from Galilee to John at the Jordan. He chose baptism to fulfill righteousness; afterward the Spirit descended like a dove, and the Father declared His love for His Son. The scene gathers those witnesses around Jesus. Baptism becomes a willing beginning: turning toward God and following the path His Son has shown."
        ],
        "sources": [
            {
                "label": "Matthew 3:13–17",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/3?lang=eng&id=p13-p17#p13"
            }
        ]
    },
    "Jesus with His Disciples at Sea": {
        "paragraphs": [
            "Waves press against the wooden boat, and the men around Jesus look toward Him with urgency. His presence holds the center of the scene while the water remains restless. The contrast makes the disciples' need for help feel immediate.",
            "In Mark 4:35–41, a storm fills the disciples' boat with water. They wake Jesus, He stills the wind and sea, and they marvel at His power. Their frightened question is part of the account, too. We can bring our own fear honestly to Him. This picture invites trust in the Savior who hears a cry for help, even before the storm has passed."
        ],
        "sources": [
            {
                "label": "Mark 4:35–41",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/mark/4?lang=eng&id=p35-p41#p35"
            }
        ]
    },
    "Jesus Feeding People": {
        "paragraphs": [
            "Bread and fish pass from Christ's hands toward people gathered on the hillside. Faces, baskets, and outstretched hands bring a great miracle close to the scale of one person's hunger. The crowd is made up of people who each need to eat.",
            "John 6:5–13 begins with a question about feeding the multitude and a boy's five barley loaves and two fish. Jesus gives thanks, the people are fed, and the remaining bread fills twelve baskets. His abundance meets an ordinary bodily need. Sharing a meal, noticing an empty cupboard, or welcoming someone to our table can become a small, sincere response to that generosity."
        ],
        "sources": [
            {
                "label": "John 6:5–13",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/6?lang=eng&id=p5-p13#p5"
            }
        ]
    },
    "Jesus Feeding the Fish": {
        "paragraphs": [
            "Small fish gather in the shallows as Jesus scatters food into the water. The gentle movement, the basket, and the people watching from the bank turn our attention to life that could easily pass unnoticed beneath the surface.",
            "This playful moment opens a reflection on care for God's creation. In Matthew 6:26–30, Jesus asks His listeners to notice birds and flowers as they learn to trust their Heavenly Father. Looking closely can become a form of gratitude. The scene encourages a kindness that reaches into small daily choices, including how we treat living things and the places we share with them."
        ],
        "sources": [
            {
                "label": "Matthew 6:26–30",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/6?lang=eng&id=p26-p30#p26"
            }
        ]
    },
    "Joy Beside the Lake": {
        "paragraphs": [
            "Jesus smiles beside a busy lakeside village, with nets, boats, and the work of the shore around Him. The setting gives joy an ordinary home. It belongs among neighbors and daily tasks, not only at the end of a difficult story.",
            "Jesus told His disciples that He wanted His joy to remain in them and their joy to be full in John 15:9–12. He connected that joy with abiding in His love and loving one another. The smile in this picture invites a grateful pause: companionship, honest work, and simple pleasures can all become occasions to receive and share the goodness of God."
        ],
        "sources": [
            {
                "label": "John 15:9–12",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/15?lang=eng&id=p9-p12#p9"
            }
        ]
    },
    "Jesus in Africa": {
        "paragraphs": [
            "Children and adults gather closely around Jesus in the shade of a tree. Patterned clothing, nearby homes, and the circle of attentive faces give this African setting warmth and life. Christ sits among the people, within their conversation and companionship.",
            "The scene brings His invitation into a community far beyond the places named in the Gospel accounts. In 2 Nephi 26:33, the invitation to come to Him includes everyone, and all are alike unto God. No nation or people stands outside His love. We can practice that welcome ourselves by honoring each person's dignity and making room for their voice."
        ],
        "sources": [
            {
                "label": "2 Nephi 26:33",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/bofm/2-ne/26?lang=eng&id=p33#p33"
            }
        ]
    },
    "The Healing Touch of Jesus": {
        "paragraphs": [
            "Jesus bends close to a man in worn clothing and reaches toward his face. The man's lowered posture and Christ's careful attention make the encounter personal. Before our eyes settle on illness, the picture asks us to notice the person being met with compassion.",
            "Mark 1:40–42 tells of a man with leprosy who asked whether Jesus was willing to make him clean. Jesus responded with compassion, touch, and healing. His willingness matters as much as His power in this encounter. For those who have felt avoided or reduced to a condition, the story offers the dignity of being seen and approached with love."
        ],
        "sources": [
            {
                "label": "Mark 1:40–42",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/mark/1?lang=eng&id=p40-p42#p40"
            }
        ]
    },
    "Learning to Forgive": {
        "paragraphs": [
            "An arm around a shoulder keeps this conversation close. Jesus gestures as the man beside Him listens, and the quiet exchange suggests teaching offered with patience. Learning a difficult way of living can begin in just such a moment of attention.",
            "In Matthew 18:21–35, Peter asks how often he should forgive. Jesus answers beyond Peter's proposed limit and tells of a servant who receives great mercy but refuses it to another. The teaching asks us to remember mercy received as we learn to offer mercy ourselves. Forgiveness can take patient work; Christ's example gives that work a direction rooted in compassion rather than keeping score."
        ],
        "sources": [
            {
                "label": "Matthew 18:21–35",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/18?lang=eng&id=p21-p35#p21"
            }
        ]
    },
    "Jesus Walking Jerusalem": {
        "paragraphs": [
            "Jesus moves through a narrow stone street among the people of the city. The walls, doorways, and seated figure at the side keep the setting human in scale. His ministry comes into places where people live, pass one another, and carry their concerns.",
            "Luke 8:1 describes Jesus traveling through cities and villages, proclaiming the good news of God's kingdom with the Twelve. Along this Jerusalem street, we can picture that ministry at walking pace, close enough for a person to approach Him. It also turns our attention toward our own familiar streets, where someone may need a greeting, a listening ear, or help that requires us to stop."
        ],
        "sources": [
            {
                "label": "Luke 8:1",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/luke/8?lang=eng&id=p1#p1"
            }
        ]
    },
    "Walking with the Apostles": {
        "paragraphs": [
            "Sunflowers line the path as Jesus walks with His companions in the evening light. Faces turn toward one another, and the shared smiles make the journey feel full of friendship. The bright field gives this devotional scene a joyful character.",
            "In John 15:12–17, Jesus calls His disciples friends and commands them to love one another. Their calling includes service and sacrifice, yet it is held within His love. The picture lets us dwell on the companionship of discipleship: people learning together, encouraging one another, and discovering that following Christ can fill a shared life with gladness."
        ],
        "sources": [
            {
                "label": "John 15:12–17",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/15?lang=eng&id=p12-p17#p12"
            }
        ]
    },
    "Little Friends": {
        "paragraphs": [
            "Two children wrap their arms around Jesus while He holds them securely. One nestles close to His face; the other rests against His shoulder. His broad smile makes their welcome unmistakable. Nothing in the moment suggests that they need to be older or more important to belong.",
            "Mark 10:13–16 tells how Jesus welcomed children when others tried to keep them away, then took them in His arms and blessed them. The embrace here gives that welcome a tender immediacy. Children deserve our attention, patience, and delight. Receiving them kindly is one way to honor the Savior who made time for them."
        ],
        "sources": [
            {
                "label": "Mark 10:13–16",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/mark/10?lang=eng&id=p13-p16#p13"
            }
        ]
    },
    "Never Alone": {
        "paragraphs": [
            "A hospital room surrounds the resting woman with the ordinary signs of medical care. Jesus sits beside her, His hand gently on her shoulder. The quiet bedside presence brings the picture's promise close to anyone who knows the long hours of illness or waiting.",
            "Alma 7:11–12 teaches that Christ took upon Himself pain, sickness, and infirmity so He could succor His people. The modern setting carries that assurance into a place many families recognize. His compassion can be remembered alongside the care of nurses, physicians, loved ones, and friends. A visit or a patient hour beside someone may help them feel less alone."
        ],
        "sources": [
            {
                "label": "Alma 7:11–12",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/bofm/alma/7?lang=eng&id=p11-p12#p11"
            }
        ]
    },
    "Now I See": {
        "paragraphs": [
            "Jesus reaches toward an older man's closed eyes while others watch from the stone passageway. The encounter is close and unhurried, with the man's face turned toward the One helping him. The picture draws our attention to the wonder of sight and the tenderness of personal care.",
            "The title recalls the witness of the man healed in John 9:1–7, 25. Jesus sent him to wash in the pool of Siloam, and he returned seeing. Later, amid questioning, he held to what he knew of the change in his life. His story invites us to value honest testimony and to keep learning from the light we have received."
        ],
        "sources": [
            {
                "label": "John 9:1–7, 25",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/9?lang=eng&id=p1-p7,p25#p1"
            }
        ]
    },
    "Palms": {
        "paragraphs": [
            "Palm branches rise behind Jesus as He lifts His open hands. The picture places two meanings of palms together: the branches of welcome and the hands extended toward us. Its inscription leads us to Isaiah's words about being remembered by the Lord.",
            "In Isaiah 49:14–16, Zion fears that God has forgotten her. The Lord answers with a mother's compassion and the image of His people graven upon His hands. That assurance gives the open hands here their tenderness. When we feel overlooked, this passage invites us to return to a love that remembers us personally and faithfully."
        ],
        "sources": [
            {
                "label": "Isaiah 49:14–16",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/ot/isa/49?lang=eng&id=p14-p16#p14"
            }
        ]
    },
    "Posterity": {
        "paragraphs": [
            "An older man and woman stand smiling with Christ's arms around their shoulders. Golden light opens behind them, and a distant gathering stretches across the background. Their familiar clothing keeps the joy personal, like the pleasure of being welcomed among people we love.",
            "Doctrine and Covenants 130:2 teaches that the relationships we enjoy here can continue with eternal glory. The picture gives that hope the warmth of recognizable faces and shared affection. We can cherish those whose love has shaped us and pass something of that love to another generation through patience, faithfulness, and everyday acts of care."
        ],
        "sources": [
            {
                "label": "Doctrine and Covenants 130:2",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/130?lang=eng&id=p2#p2"
            }
        ]
    },
    "Suffer the Little Children": {
        "paragraphs": [
            "Six children gather around Jesus beneath the olive trees, two holding small white flowers. They have room to sit close, smile, and be themselves. His open gesture welcomes their company, and the scene feels as peaceful as an afternoon spent with someone who is glad to see them.",
            "In Mark 10:13–16, the word suffer means to allow: Jesus tells His disciples to let the children come. He receives and blesses them rather than treating them as an interruption. The flowers and smiling faces help us linger over that welcome. Giving a child our full attention can turn a simple moment into a lasting experience of love."
        ],
        "sources": [
            {
                "label": "Mark 10:13–16",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/mark/10?lang=eng&id=p13-p16#p13"
            }
        ]
    },
    "The Garden": {
        "paragraphs": [
            "Jesus kneels against an olive tree in the darkness, His hands clasped and His face drawn with sorrow. Three companions rest behind Him. The stillness of the garden makes His solitary prayer feel especially weighty.",
            "Matthew 26:36–46 records His prayer in Gethsemane, His request that the disciples watch with Him, and His submission to the Father's will. This is a moment for reverent attention to the Savior's willing sacrifice. His suffering gives depth to our trust in Him: the One to whom we bring anguish has entered anguish Himself, and His love did not turn away from the work of redemption."
        ],
        "sources": [
            {
                "label": "Matthew 26:36–46",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/26?lang=eng&id=p36-p46#p36"
            }
        ]
    },
    "The Good Shepherd": {
        "paragraphs": [
            "The Savior's smile meets us in the middle of a busy market street. People, stalls, and a laden donkey remain behind Him, but His face is the point of welcome. The title brings shepherding into a scene of ordinary human life.",
            "In John 10:11–15, Jesus calls Himself the Good Shepherd who knows His sheep and gives His life for them. His care is personal and costly. Here that teaching can be felt in the simple thought of being recognized amid a crowd. Following His voice means learning to trust His love and to extend attentive care to people who might otherwise go unnoticed."
        ],
        "sources": [
            {
                "label": "John 10:11–15",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/10?lang=eng&id=p11-p15#p11"
            }
        ]
    },
    "The Living Christ": {
        "paragraphs": [
            "Light fills the sky behind this close portrait, but the warmth of Christ's face holds our attention. His smile gives the title a feeling of welcome and life. We are invited to think of a Savior whose relationship with His disciples continues beyond the events of His mortal ministry.",
            "John 20:19–20 tells how the risen Jesus came to His disciples, offered peace, and showed them His hands and side. Their fear gave way to gladness when they saw Him. This portrait is a quiet place to remember that joyful witness and the Christian hope it carries: Jesus Christ lives, and His love remains a source of peace."
        ],
        "sources": [
            {
                "label": "John 20:19–20",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/20?lang=eng&id=p19-p20#p19"
            }
        ]
    },
    "Tranquil Morning": {
        "paragraphs": [
            "A girl sits beside Jesus at the water's edge while ducks and ducklings gather for food. Their feet rest near the pond, and the rising sun spreads across the water. His arm around her and their shared smiles make this small activity feel precious.",
            "In Matthew 6:26–30, Jesus draws attention to birds and flowers when teaching about the Father's care. The picture turns that attentiveness into a quiet morning together. Wonder often begins with something small: a moving ripple, a hungry duckling, a child's delight. Taking time to notice can help gratitude become part of the way we live."
        ],
        "sources": [
            {
                "label": "Matthew 6:26–30",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/6?lang=eng&id=p26-p30#p26"
            }
        ]
    },
    "The Widow's Mite": {
        "paragraphs": [
            "The older woman's hand reaches toward the offering box with a small coin, while other people stand nearby with their gifts. Jesus is close in the composition, drawing our attention to someone whose offering might otherwise seem slight.",
            "Mark 12:41–44 records that Jesus watched the treasury and called His disciples to notice a poor widow's two small coins. He understood what her gift cost her. The account encourages a deeper kind of attention: generosity cannot be measured by size alone. A modest gift, a careful act of service, or time freely given may carry love that is easy to miss."
        ],
        "sources": [
            {
                "label": "Mark 12:41–44",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/mark/12?lang=eng&id=p41-p44#p41"
            }
        ]
    },
    "Let It Go": {
        "paragraphs": [
            "The man beside Jesus looks weighed down as they walk a sunlit hillside path. Christ rests a hand on his shoulder and turns toward him. The gesture offers company while the man's expression remains thoughtful; the picture allows a burden to be acknowledged before it is released.",
            "Matthew 11:28–30 invites the weary to come to Christ and learn from Him. The invitation is gentle, and it asks for a relationship of trust. Letting go may begin with an honest prayer, accepting help, or taking one faithful step instead of trying to solve everything at once. The road ahead is still there, but the man no longer walks it alone."
        ],
        "sources": [
            {
                "label": "Matthew 11:28–30",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/11?lang=eng&id=p28-p30#p28"
            }
        ]
    },
    "Be Still": {
        "paragraphs": [
            "The city keeps moving around a man in a dark T-shirt and the Savior walking beside him. Christ's hand rests on his shoulder as they look toward one another. Their conversation creates a small place of attention within the crowd.",
            "Psalm 46:1–10 speaks of God's refuge amid upheaval and calls His people to be still and know Him. The modern street brings that invitation into a busy day. Stillness may begin as a moment of prayer or a deliberate pause before the next demand. We can learn to turn toward God while life continues around us, receiving enough peace to meet the next person with care."
        ],
        "sources": [
            {
                "label": "Psalm 46:1–10",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/ot/ps/46?lang=eng&id=p1-p10#p1"
            }
        ]
    },
    "The Savior's Invitation": {
        "paragraphs": [
            "An open hand reaches toward us beside the water, with the evening sky glowing behind Christ. His face and gesture make the invitation personal. There is space in the picture for the viewer to become part of the encounter.",
            "Matthew 11:28–30 records His invitation to those who labor and are burdened. Coming to Him includes learning from His meekness and trusting His care. The outstretched hand encourages a beginning wherever we are today. We do not need perfect words for a first prayer or complete understanding before we take a sincere step toward Him."
        ],
        "sources": [
            {
                "label": "Matthew 11:28–30",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/11?lang=eng&id=p28-p30#p28"
            }
        ]
    },
    "Rest in the Lord, Trust in the Lord": {
        "paragraphs": [
            "Children run along a path through sunflowers while Christ extends His hand toward us. Warm light, growing things, and the freedom of their movement give the scene a sense of welcome. Rest here has room for gladness and life.",
            "Psalm 37:3–7 joins trust with doing good, committing our way to God, and waiting patiently for Him. The picture draws those ideas together in a bright invitation. Trust can free us to keep doing the good that is within reach, even when we cannot settle every concern. A moment of delight may become one way to receive the day as a gift."
        ],
        "sources": [
            {
                "label": "Psalm 37:3–7",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/ot/ps/37?lang=eng&id=p3-p7#p3"
            }
        ]
    },
    "See That Ye Be Not Troubled": {
        "paragraphs": [
            "Lightning, dark clouds, and distant fires fill the landscape behind Jesus. His open hand reaches into the foreground, nearer than the turmoil. The contrast gives the picture its steady center without hiding the troubled world around Him.",
            "In Matthew 24:4–8, Jesus warns His disciples about deception and news of wars, while cautioning them against alarm and hasty conclusions. His steady presence in the picture gives those words a personal warmth. We can seek trustworthy understanding, care for those affected by suffering, and continue following Christ without letting every frightening report decide the condition of our hearts."
        ],
        "sources": [
            {
                "label": "Matthew 24:4–8",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/24?lang=eng&id=p4-p8#p4"
            }
        ]
    },
    "Joy Cometh in the Morning": {
        "paragraphs": [
            "A woman and child hold each other close among the flowers, their faces bright with affection. Jesus stands behind them with a smile. The embrace makes joy feel tangible: the warmth of another person, a welcome held for a little longer.",
            "Psalm 30:5, 11–12 moves from weeping to renewed gladness and thanksgiving. Its hope gives the morning light in this picture a deeper meaning. Joy can return to a life that has known sorrow, sometimes in quiet and unexpected ways. We can cherish those moments without rushing anyone's grief or placing a deadline on healing."
        ],
        "sources": [
            {
                "label": "Psalm 30:5, 11–12",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/ot/ps/30?lang=eng&id=p5,p11-p12#p5"
            }
        ]
    },
    "Blessed Be the Name of the Lord": {
        "paragraphs": [
            "Jesus sits among sunflowers with His arm around another man. The man's face turns toward Him, and their closeness gives warmth to the solemn words above them. The scene invites us to think about companionship in seasons when gratitude and sorrow meet.",
            "Job 1:20–22 places Job's blessing of the Lord alongside his grief after devastating loss. His worship does not erase his mourning. Bringing these words beside Christ's embrace offers a reflection on faith that can speak honestly through pain. We may hold tightly to God while also receiving comfort, asking difficult questions, and accepting the help of people who care."
        ],
        "sources": [
            {
                "label": "Job 1:20–22",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/ot/job/1?lang=eng&id=p20-p22#p20"
            }
        ]
    },
    "There Is a Green Hill Far Away": {
        "paragraphs": [
            "Christ stands before a walled city with three crosses on a distant hill. The quiet foreground and the far-off crosses bring His living presence and His sacrifice into one reflective composition. The green mantle and subdued expression keep the mood reverent.",
            "Cecil Frances Alexander's hymn There Is a Green Hill Far Away directs our thoughts to the Savior's redeeming love. John 19:16–20 records His Crucifixion at Golgotha, near the city. The picture invites a grateful response to that sacrifice: trust in Him, remembrance of His love, and a willingness to let that love shape how we treat others."
        ],
        "sources": [
            {
                "label": "There Is a Green Hill Far Away",
                "href": "https://www.churchofjesuschrist.org/study/manual/hymns/there-is-a-green-hill-far-away?lang=eng"
            },
            {
                "label": "John 19:16–20",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/19?lang=eng&id=p16-p20#p16"
            }
        ]
    },
    "Make a Joyful Noise Unto God": {
        "paragraphs": [
            "Laughter passes through the gathering beside the stream. Children lean close to Jesus, and the adults share their delight among the flowers. The scene gives us a welcome reminder that joy and reverence can belong together.",
            "Psalm 66:1–5 calls the whole earth to praise God and come see His works. Here the invitation finds an echo in shared happiness and gratitude for life. Praise can be sung, spoken, or lived through generous attention to another person. The picture encourages us to receive wholesome joy gladly and let gratitude become something we share."
        ],
        "sources": [
            {
                "label": "Psalm 66:1–5",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/ot/ps/66?lang=eng&id=p1-p5#p1"
            }
        ]
    },
    "In the Name of the Lord of Hosts": {
        "paragraphs": [
            "The boy holds a sling while an armored warrior towers behind him. Christ's hands rest on the boy's shoulders, bringing reassurance into a scene of danger. The composition gives visible form to the courage of trusting the Lord when the odds seem overwhelming.",
            "In 1 Samuel 17:40–47, David faces Goliath with a sling and confidence in the God of Israel. The picture brings that ancient testimony together with a Christian reflection on the Savior's sustaining presence. Its strongest invitation is to trust God while acting faithfully with the means we have, rather than measuring every challenge only by its size."
        ],
        "sources": [
            {
                "label": "1 Samuel 17:40–47",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/ot/1-sam/17?lang=eng&id=p40-p47#p40"
            }
        ]
    },
    "There Is a Greater Victory Ahead": {
        "paragraphs": [
            "A heavily armed warrior stands before the Savior's outstretched hand. The spear and armor suggest a life prepared for conflict; Christ offers another direction with a gentle, open gesture. The picture places a choice before us rather than showing a battle won.",
            "The words from Matthew 11:28–30 turn our attention toward rest, meekness, and learning from Jesus. In this scene, a greater victory can be understood as accepting His invitation and allowing a life to change. Courage may be needed to loosen our grip on pride or anger and choose the patient work of becoming more like Him."
        ],
        "sources": [
            {
                "label": "Matthew 11:28–30",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/11?lang=eng&id=p28-p30#p28"
            }
        ]
    },
    "His Strength and Redeeming Power": {
        "paragraphs": [
            "The picture moves from a bowed figure in shadow toward a woman rising into golden light beneath Christ's welcoming arms. That upward movement gives a visual language to hope and renewal. The Savior's open hands remain the center of the change.",
            "In Overcome the World and Find Rest, President Russell M. Nelson taught that a covenant relationship with Jesus Christ gives access to His strengthening and redeeming power. He also made clear that covenants do not remove all opposition. We can seek that strength through faithful connection with Him, remembering that spiritual growth can continue even while difficult circumstances remain."
        ],
        "sources": [
            {
                "label": "Overcome the World and Find Rest",
                "href": "https://www.churchofjesuschrist.org/study/general-conference/2022/10/47nelson?lang=eng"
            }
        ]
    },
    "God Will Feel After You": {
        "paragraphs": [
            "Jesus walks beside a stream toward a sunlit tree, with rough ground still beneath His feet. The path and the flowing water give the picture a sense of continuing onward. Its light offers hope beside words that speak seriously about trials.",
            "In Stand Fast through the Storms of Life, John Taylor recalls Joseph Smith teaching the Twelve that faith would be tested deeply. The chapter also preserves Joseph's confidence that God would support His people in affliction. Read together, these teachings encourage faithful endurance sustained by divine help. As we keep walking with Christ, we can offer companionship to those whose present path is hard."
        ],
        "sources": [
            {
                "label": "Stand Fast through the Storms of Life",
                "href": "https://www.churchofjesuschrist.org/study/manual/teachings-joseph-smith/chapter-19?lang=eng"
            }
        ]
    },
    "Jesus Christ": {
        "paragraphs": [
            "The portrait brings us close to the Savior's face, with the evening landscape softly behind Him. His attentive gaze and gentle expression invite a quiet pause. There is no crowd or dramatic action to follow, only the opportunity to turn our attention toward Him.",
            "In John 14:6–9, Jesus teaches that He is the way to the Father and that knowing Him reveals the Father. A portrait can begin a moment of reflection, while His words and life deepen it. As we study His compassion, truthfulness, and willing service, we come to know more of the love He invites us to receive and practice."
        ],
        "sources": [
            {
                "label": "John 14:6–9",
                "href": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/14?lang=eng&id=p6-p9#p6"
            }
        ]
    }
};

    const FEATURED = {
        'The Living Christ': { focus: 'art-study/the-living-christ.html', query: 'The Living Christ Jesus Christ Atonement Resurrection' },
        'The Good Shepherd': { focus: 'art-study/the-good-shepherd.html', query: 'Good Shepherd Jesus Christ John 10' },
        'Suffer the Little Children': { focus: 'art-study/suffer-the-little-children.html', query: 'Jesus Christ children suffer little children' },
        'Be Still': { focus: 'art-study/be-still.html', query: 'Be still Psalm 46 trust God Jesus Christ' }
    };

    const SCENE_HINTS = [
        { match: ['Divine Push'], query: 'Jesus Christ guidance discipleship trust God' },
        { match: ['Forever Friends', 'Forever', 'Posterity'], query: 'eternal families Jesus Christ resurrection family relationships' },
        { match: ['Jesus and Mary His Mom'], query: 'Mary mother of Jesus Christ New Testament' },
        { match: ['Jesus Baptized'], query: 'baptism of Jesus Christ Matthew 3' },
        { match: ['Jesus Boat'], query: 'Jesus Christ calms the storm Mark 4 faith' },
        { match: ['Jesus Feeding People'], query: 'Jesus Christ feeding five thousand John 6' },
        { match: ['Jesus Feeding the Fish'], query: "Jesus Christ kindness caring for God's creations" },
        { match: ['Jesus Fun', 'Little Friends'], query: 'Jesus Christ joy children discipleship' },
        { match: ['Jesus in Africa'], query: 'Jesus Christ all nations children of God' },
        { match: ['Jesus Leper', 'Now I See'], query: 'Jesus Christ healing miracles faith New Testament' },
        { match: ['Jesus Seven Times Seven', 'Let It Go'], query: 'Jesus Christ forgiveness seventy times seven Matthew 18' },
        { match: ['Palms'], query: 'Jesus Christ Isaiah 49:16 remembered not forgotten' },
        { match: ['Jesus Walking Jerusalem'], query: 'Jesus Christ ministry Jerusalem disciples' },
        { match: ['Jesus with Apostles Sunflowers'], query: 'Jesus Christ Apostles disciples teachings' },
        { match: ['Never Alone'], query: 'Jesus Christ comfort never alone Holy Ghost' },
        { match: ['Widows Mite'], query: "widow's mite Jesus Christ Mark 12 sacrifice" },
        { match: ['The Garden', 'There Is a Green Hill Far Away'], query: 'Jesus Christ Gethsemane Crucifixion Atonement Resurrection' },
        { match: ["The Savior's Invitation"], query: 'Jesus Christ invitation come unto me discipleship' },
        { match: ['Rest in the Lord, Trust in the Lord'], query: 'rest in the Lord trust in the Lord Psalm 37' },
        { match: ['See That Ye Be Not Troubled'], query: 'see that ye be not troubled Matthew 24 Jesus Christ' },
        { match: ['Joy Cometh in the Morning'], query: 'joy cometh in the morning Psalm 30 Jesus Christ hope' },
        { match: ['Blessed Be the Name of the Lord'], query: 'blessed be the name of the Lord Job 1 faith adversity' },
        { match: ['Make a Joyful Noise Unto God'], query: 'make a joyful noise unto God Psalm 66 worship praise' },
        { match: ['In the Name of the Lord of Hosts'], query: 'David Goliath 1 Samuel 17 Lord of hosts faith' },
        { match: ['There Is a Greater Victory Ahead'], query: 'Jesus Christ victory hope adversity faith' },
        { match: ['His Strength and Redeeming Power'], query: 'Jesus Christ redeeming power strength Atonement' },
        { match: ['God Will Feel After You'], query: 'God feel after you Joseph Smith seek God revelation' },
        { match: ['Tranquil Morning'], query: 'Jesus Christ peace prayer stillness morning devotion' }
    ];

    function captionForItem(item) {
        const caption = item ? item.querySelector('.caption') : null;
        return caption ? caption.textContent.trim() : '';
    }

    function routeForCaption(caption) {
        const legacy = Object.keys(TITLE_ALIASES).find(function (key) { return TITLE_ALIASES[key] === caption; }) || caption;
        if (FEATURED[caption]) return Object.assign({ caption: caption }, FEATURED[caption]);
        const hint = SCENE_HINTS.find(function (entry) { return entry.match.includes(legacy); });
        const query = hint ? hint.query : (caption || 'Jesus Christ');
        return { caption: caption || 'This artwork', focus: '', query: query };
    }

    function officialSearch(query) {
        return CHURCH_SEARCH + encodeURIComponent(query || 'Jesus Christ');
    }

    function returnUrlForCaption(caption) {
        return 'art.html?art=' + encodeURIComponent(caption || 'This artwork');
    }

    function askUrl(route) {
        const params = new URLSearchParams();
        params.set('art', route.caption);
        params.set('topic', route.query || route.caption);
        params.set('return', returnUrlForCaption(route.caption));
        return 'ask.html?' + params.toString() + '#ask-question';
    }

    function ensureStyles() {
        if (document.getElementById('focuschrist-art-study-router-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-art-study-router-styles';
        style.textContent = `
            .fc-art-study-button{position:absolute;left:22px;bottom:18px;z-index:1002;min-height:42px;padding:8px 15px;border:1px solid var(--fc-line-strong);border-radius:999px;background:var(--fc-bg-warm);color:var(--fc-gold-light);font:inherit;font-size:.82rem;font-weight:700;cursor:pointer;backdrop-filter:blur(8px)}
            .fc-art-study-button:hover,.fc-art-study-button:focus-visible{background:var(--fc-surface);color:var(--fc-cream);outline:none}
            .fc-art-study-drawer{position:absolute;left:18px;right:18px;bottom:72px;z-index:1003;display:none;max-width:780px;margin:0 auto;padding:16px;border:1px solid var(--fc-line);border-radius:14px;background:var(--fc-bg-deep);box-shadow:var(--fc-shadow);cursor:default}
            #imageModal .fc-art-viewer-actions{position:absolute;left:max(12px,env(safe-area-inset-left));right:max(12px,env(safe-area-inset-right));bottom:max(18px,env(safe-area-inset-bottom));display:grid;grid-template-columns:1.2fr 1.1fr 1fr;gap:8px;max-width:560px;margin:0 auto;z-index:1002;cursor:default}
            #imageModal .fc-art-viewer-actions>*{position:static;transform:none;box-sizing:border-box;display:flex;align-items:center;justify-content:center;min-width:0;width:100%;height:auto;min-height:44px;margin:0;padding:6px;border:1px solid var(--fc-line-strong);border-radius:999px;background:var(--fc-bg-warm);color:var(--fc-cream);font:inherit;font-size:.78rem;font-weight:700;line-height:1.2;text-align:center;text-decoration:none;white-space:normal;overflow-wrap:anywhere;cursor:pointer;backdrop-filter:blur(8px)}
            #imageModal .fc-art-viewer-actions>*:hover,#imageModal .fc-art-viewer-actions>*:focus-visible{background:var(--fc-surface);color:var(--fc-cream);outline:3px solid var(--fc-line-strong);outline-offset:2px}
            #imageModal .image-counter{bottom:calc(max(18px,env(safe-area-inset-bottom)) + var(--fc-art-actions-height,44px) + 8px);font-size:.8rem;line-height:1.2;pointer-events:none;width:fit-content;padding:4px 8px;border-radius:999px;background:var(--fc-bg-warm)}
            #imageModal .fc-art-study-drawer{bottom:calc(max(18px,env(safe-area-inset-bottom)) + var(--fc-art-actions-height,44px) + 24px + .96rem);max-height:calc(100dvh - max(18px,env(safe-area-inset-bottom)) - var(--fc-art-actions-height,44px) - 24px - .96rem - 18px);overflow-y:auto;box-sizing:border-box}
            .fc-art-study-drawer.open{display:block}
            .fc-art-study-title{margin:0 0 8px;color:var(--fc-gold-light);font-family:var(--fc-font-display);font-size:1.15rem}
            .fc-art-study-copy{margin:0 0 16px;color:var(--fc-text);font-size:.84rem;line-height:1.55}
            .fc-art-study-links{display:flex;flex-wrap:wrap;gap:8px}
            .fc-art-study-links a{box-sizing:border-box;min-width:0;white-space:normal;overflow-wrap:anywhere;display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 13px;border:1px solid var(--fc-line);border-radius:999px;background:var(--fc-surface-soft);color:var(--fc-gold-light)!important;text-decoration:none!important;font-size:.77rem;font-weight:700}
            .fc-art-study-links a[data-art-ask]{background:var(--fc-action-fill);color:var(--fc-action-text)!important;border-color:var(--fc-gold-light)}
            .fc-art-study-links a:hover,.fc-art-study-links a:focus-visible{background:var(--fc-surface-hover);border-color:var(--fc-gold-light);outline:none}
            .fc-art-study-links a[data-art-ask]:hover,.fc-art-study-links a[data-art-ask]:focus-visible{background:var(--fc-action-hover);color:var(--fc-action-text)!important}
            .fc-art-study-hint{max-width:760px;margin:0 auto 6px;padding:0 18px;color:var(--fc-muted);font-size:.82rem;text-align:center}
            @media(max-width:700px){.fc-art-study-button{left:12px;bottom:12px}.fc-art-study-drawer{left:10px;right:10px;bottom:62px;padding:13px}.fc-art-study-links{display:grid}.fc-art-study-links a{width:100%}}
        `;
        document.head.appendChild(style);
    }

    function ensureHint() {
        const gallery = document.querySelector('.gallery');
        if (!gallery || document.querySelector('[data-focuschrist-art-study-hint]')) return;
        const hint = document.createElement('p');
        hint.className = 'fc-art-study-hint';
        hint.setAttribute('data-focuschrist-art-study-hint', 'true');
        hint.textContent = 'Open a picture and choose About this picture to read its story, explore the scripture behind it, and linger with what speaks to you.';
        gallery.insertAdjacentElement('beforebegin', hint);
    }

    function currentGalleryItem() {
        const modalImage = document.getElementById('modalImage');
        if (!modalImage) return null;
        const currentSrc = modalImage.getAttribute('src') || '';
        const items = Array.from(document.querySelectorAll('.gallery-item'));
        return items.find(function (item) {
            const img = item.querySelector('img');
            if (!img) return false;
            const full = img.getAttribute('data-full-src') || img.getAttribute('src') || '';
            return full === currentSrc || img.getAttribute('src') === currentSrc;
        }) || null;
    }

    function syncArtworkUrl(caption) {
        if (!caption || !window.history || typeof window.history.replaceState !== 'function') return;
        const url = new URL(window.location.href);
        url.searchParams.set('art', caption);
        url.hash = '';
        window.history.replaceState(null, '', url.pathname + '?' + url.searchParams.toString());
    }

    function appendLinkedText(parent, text, sources) {
        let remaining = text;
        while (remaining) {
            const matches = sources.map(function (source) {
                return { source: source, index: remaining.indexOf(source.label) };
            }).filter(function (match) { return match.index >= 0; });
            matches.sort(function (a, b) {
                return a.index - b.index || b.source.label.length - a.source.label.length;
            });
            const match = matches[0];
            if (!match) {
                parent.appendChild(document.createTextNode(remaining));
                break;
            }
            parent.appendChild(document.createTextNode(remaining.slice(0, match.index)));
            const link = document.createElement('a');
            link.href = match.source.href;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = match.source.label;
            parent.appendChild(link);
            remaining = remaining.slice(match.index + match.source.label.length);
        }
    }

    function buildDrawer(drawer, route) {
        drawer.replaceChildren();
        const title = document.createElement('h3');
        title.className = 'fc-art-study-title';
        title.textContent = route.caption;
        drawer.appendChild(title);

        const story = PICTURE_STORIES[route.caption];
        const paragraphs = story ? story.paragraphs : [document.getElementById('modalImage').alt];
        const sources = story ? story.sources : [];
        paragraphs.forEach(function (paragraph) {
            const copy = document.createElement('p');
            copy.className = 'fc-art-study-copy';
            appendLinkedText(copy, paragraph, sources);
            drawer.appendChild(copy);
        });

        const links = document.createElement('div');
        links.className = 'fc-art-study-links';

        sources.forEach(function (source) {
            const link = document.createElement('a');
            link.href = source.href;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = source.label;
            link.setAttribute('data-art-picture-source', 'true');
            links.appendChild(link);
        });

        if (route.focus) {
            const focus = document.createElement('a');
            focus.href = route.focus;
            focus.textContent = 'Read the related study';
            focus.setAttribute('data-art-focus-study', 'true');
            links.appendChild(focus);
        }

        drawer.appendChild(links);
    }

    function refreshModalRoute(drawer) {
        const item = currentGalleryItem();
        const save = document.getElementById('artSaveImage');
        const image = document.getElementById('modalImage');
        if (save && image) {
            save.href = image.src;
            save.download = window.fcArtworkDownloadFilename(captionForItem(item) || image.alt || 'Artwork', image.src);
        }
        const caption = captionForItem(item) || 'This artwork';
        const route = routeForCaption(caption);
        buildDrawer(drawer, route);
        if (document.getElementById('imageModal')?.classList.contains('active')) syncArtworkUrl(caption);
    }

    function initModalStudy() {
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        if (!modal || !modalImage || modal.querySelector('[data-focuschrist-art-study-button]')) return;

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'fc-art-study-button';
        button.setAttribute('data-focuschrist-art-study-button', 'true');
        button.textContent = 'About this picture';

        const drawer = document.createElement('aside');
        drawer.className = 'fc-art-study-drawer';
        drawer.id = 'artPictureDetails';
        button.setAttribute('aria-controls', drawer.id);
        drawer.setAttribute('data-focuschrist-art-study-drawer', 'true');
        drawer.setAttribute('aria-live', 'polite');

        button.addEventListener('click', function (event) {
            event.stopPropagation();
            refreshModalRoute(drawer);
            drawer.classList.toggle('open');
            button.setAttribute('aria-expanded', drawer.classList.contains('open') ? 'true' : 'false');
        });
        button.setAttribute('aria-expanded', 'false');

        // Let the shared scripture reader receive source-link clicks.
        // The artwork backdrop closes only when its own surface is clicked.
        const actions = document.createElement('div');
        actions.className = 'fc-art-viewer-actions';
        const save = document.createElement('a');
        save.id = 'artSaveImage';
        save.textContent = 'Save image';
        save.setAttribute('download', '');
        actions.appendChild(button);
        actions.appendChild(save);
        const close = modal.querySelector('.close');
        if (close) actions.appendChild(close);
        modal.appendChild(actions);
        modal.appendChild(drawer);

        function syncActionLayout() {
            const height = Math.ceil(actions.getBoundingClientRect().height);
            if (height > 0) modal.style.setProperty('--fc-art-actions-height', height + 'px');
        }
        if (typeof ResizeObserver === 'function') {
            new ResizeObserver(syncActionLayout).observe(actions);
        }
        window.addEventListener('resize', syncActionLayout);

        const observer = new MutationObserver(function () {
            if (modal.classList.contains('active')) {
                syncActionLayout();
                refreshModalRoute(drawer);
            }
            else {
                drawer.classList.remove('open');
                button.setAttribute('aria-expanded', 'false');
            }
        });
        observer.observe(modalImage, { attributes: true, attributeFilter: ['src'] });
        observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
    }

    function restoreRequestedArtwork() {
        const params = new URLSearchParams(window.location.search);
        const requested = params.get('art');
        if (!requested || typeof window.openModal !== 'function') return;
        const oldTitle = Object.keys(TITLE_ALIASES).find(function (key) { return key.toLowerCase() === requested.trim().toLowerCase(); });
        const resolved = oldTitle ? TITLE_ALIASES[oldTitle] : requested.trim();
        const item = Array.from(document.querySelectorAll('.gallery-item')).find(function (candidate) {
            return captionForItem(candidate).toLowerCase() === resolved.toLowerCase();
        });
        if (!item) return;
        window.setTimeout(function () {
            try { item.scrollIntoView({ block: 'center', behavior: 'auto' }); } catch (_error) { item.scrollIntoView(); }
            window.openModal(item);
            document.documentElement.setAttribute('data-focuschrist-art-return-restored', 'true');
        }, 80);
    }

    function init() {
        ensureStyles();
        ensureHint();
        initModalStudy();
        restoreRequestedArtwork();
        document.documentElement.setAttribute('data-focuschrist-art-study-router', 'ready');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
