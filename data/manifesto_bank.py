"""
Panchayat Manifesto Bank
========================
A centralized repository of political promises and their 
hardcoded effects on the voter population (0-4 groups).
"""

MANIFESTO_BANK = [
    {
        "id": 211,
        "title": "Gaon Jal Sanrakshan Mission",
        "description": "Har gaon mein check dam, talaab sudhar aur rainwater harvesting pranali lagaakar kheti aur peene ke paani ki sthayi vyavastha ki jayegi.",
        "dialogue": "Mere kisan bhaiyo, paani ke bina kheti adhoori hai aur jeevan bhi. Hamari sarkar har boond bachayegi, har khet tak paani pahunchayegi. Yeh mera vaada nahi, aapke adhikar ki ladai hai.",
        "speech_style": "visionary",
        "target_group_id": 0,
        "shift_amount": 3.4,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 212,
        "title": "Yuva Rozgar Internship Yojana",
        "description": "Har zila mein private aur sarkari sansthaon ke saath paid internship program chalakar yuvaon ko rojgar ke liye taiyar kiya jayega.",
        "dialogue": "Hamare yuva sirf degree lekar ghar na baithein, unhe kaam ka mauka milega. Main chahta hoon ki har yuva ke haath mein hunar ho aur jeb mein izzat ki kamai. Rozgar ab sapna nahi, haq hoga.",
        "speech_style": "inspirational",
        "target_group_id": 4,
        "shift_amount": 4.1,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 213,
        "title": "Kisan Minimum Storage Guarantee",
        "description": "Chhote kisanon ke liye sarkari godaam aur cold storage uplabdh karaye jayenge taaki ve turant sasti bikri ke liye majboor na hon.",
        "dialogue": "Kisan apni fasal ugata hai, lekin majboori mein saste daam par bech deta hai. Main is anyaay ko khatam karunga. Ab fasal ka daam bazaar nahi, kisan ki izzat tay karegi.",
        "speech_style": "grassroots",
        "target_group_id": 0,
        "shift_amount": 3.8,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 214,
        "title": "Nayi Peedhi Coding Kendras",
        "description": "Har block star par coding, AI aur digital skills sikhane ke liye free training kendr sthapit kiye jayenge.",
        "dialogue": "Mere pyare bachcho aur yuva saathiyo, main chahti hoon ki gaon ka beta-beti bhi duniya ki badi technology se jude. Hunar sheharon tak simit nahi rahega. Main har ghar se ek digital sapna nikalte dekhna chahti hoon.",
        "speech_style": "inspirational",
        "target_group_id": 1,
        "shift_amount": 4.3,
        "archetype_suitability": "mukti_devi",
        "used_by": None
    },
    {
        "id": 215,
        "title": "Smart Panchayat Dashboard",
        "description": "Har panchayat ke kharch, yojana aur kaam ki sthiti ko ek digital dashboard par janata ke liye khula rakha jayega.",
        "dialogue": "Ab sarkar band kamron mein nahi chalegi, janata ke saamne chalegi. Har paisa kahan laga, har kaam kitna hua — sab aap dekh paayenge. Yeh hai asli imaandaar shasan.",
        "speech_style": "reformist",
        "target_group_id": 2,
        "shift_amount": 2.9,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 216,
        "title": "Mazdoor Awas Adhikar Abhiyan",
        "description": "Shahri aur gramin mazdoor parivaron ke liye kam daam par surakshit rental housing aur basic suvidhaon ka vikas kiya jayega.",
        "dialogue": "Jo desh banata hai, us mazdoor ke paas khud ka surakshit ghar kyun na ho? Main mazdoor parivaron ko izzat ke saath rehne ka adhikar dilakar rahungi. Gareebi ko majboori nahi, itihaas banana hoga.",
        "speech_style": "emotional",
        "target_group_id": 3,
        "shift_amount": 4.6,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 217,
        "title": "Yuva Sports Scholarship Card",
        "description": "Pratibhashali yuva khiladiyon ko training, diet, travel aur equipment ke liye state scholarship di jayegi.",
        "dialogue": "Talent gaon ke maidan mein bhi hota hai, bas mauka nahi milta. Main har yuva khiladi ko woh sahara dunga jisse woh rajya aur desh ka naam roshan kare. Medal tab aata hai jab sarkar khiladi ke saath khadi ho.",
        "speech_style": "inspirational",
        "target_group_id": 4,
        "shift_amount": 3.7,
        "archetype_suitability": "all",
        "used_by": None
    },
    {
        "id": 218,
        "title": "Beej Suraksha Kendras",
        "description": "Har tehsil mein certified beej, mitti parikshan aur kheti salaah ke liye ek integrated kisan seva kendra khola jayega.",
        "dialogue": "Kheti andaze se nahi, vigyaan se chalegi. Hamare kisan ko behtar beej, sahi jaankari aur mazboot sahara milega. Jab kisan majboot hoga tabhi desh samruddh hoga.",
        "speech_style": "reformist",
        "target_group_id": 0,
        "shift_amount": 3.1,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 219,
        "title": "Rashtra Vidya Tablet Yojana",
        "description": "Garib aur mehanati chhatron ko online padhai, test series aur digital notes ke liye subsidized tablets diye jayenge.",
        "dialogue": "Main nahi chahti ki kisi bachche ka sapna paise ki kami se ruk jaaye. Har mehanati vidyarthi ke haath mein padhai ka hathiyar hoga. Shiksha ab suvidha nahi, sabka adhikar hogi.",
        "speech_style": "compassionate",
        "target_group_id": 1,
        "shift_amount": 4.0,
        "archetype_suitability": "mukti_devi",
        "used_by": None
    },
    {
        "id": 220,
        "title": "Startup Gaon Incubation Grid",
        "description": "Tier-2 aur Tier-3 shahron mein startup incubation hub banaakar local innovation aur employment ko badhava diya jayega.",
        "dialogue": "Naye Bharat ka vikas sirf metro shehron se nahi hoga, chhote shahron se bhi hoga. Main chahta hoon har yuva job dhoondhne wala nahi, job dene wala bane. Soch ko startup aur sapne ko system milega.",
        "speech_style": "visionary",
        "target_group_id": 2,
        "shift_amount": 4.4,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 221,
        "title": "Shramik Bachcha Shiksha Suraksha",
        "description": "Mazdoor parivaron ke bachchon ke liye free school kit, scholarship aur hostel sahayata sunischit ki jayegi.",
        "dialogue": "Mazdoor ka bachcha bhi doctor, engineer aur officer ban sakta hai — aur main is sapne ko sach karungi. Gareebi ko padhai ke raaste mein deewar nahi banne dungi. Har bachcha meri zimmedari hai.",
        "speech_style": "compassionate",
        "target_group_id": 3,
        "shift_amount": 4.2,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 222,
        "title": "Nasha Mukti Yuva Kendras",
        "description": "Har zila mein counseling, sports aur career guidance ke madhyam se yuvaon ko nasha se door rakhne ke kendr sthapit kiye jayenge.",
        "dialogue": "Hamare yuva desh ka bhavishya hain, unhe barbaadi ki raah par nahi jaane denge. Main chahti hoon har yuva ke paas maidan ho, margdarshan ho aur ek nayi disha ho. Nasha nahi, nayi soch chahiye.",
        "speech_style": "emotional",
        "target_group_id": 4,
        "shift_amount": 3.6,
        "archetype_suitability": "dharma_rakshak",
        "used_by": None
    },
    {
        "id": 223,
        "title": "Gaon to Market Express",
        "description": "Kisan utpad ko seedha mandi aur shahri bazaar tak pahunchane ke liye subsidized transport corridor tayar kiya jayega.",
        "dialogue": "Kisan ki mehnat raste mein barbaad nahi hone denge. Gaon ka maal seedha bazaar tak jayega aur behtar daam lekar aayega. Yeh sadak nahi, samruddhi ka raasta hai.",
        "speech_style": "visionary",
        "target_group_id": 0,
        "shift_amount": 3.9,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 224,
        "title": "Competitive Exam Hostel Scheme",
        "description": "JEE, NEET, UPSC aur sarkari naukri ki tayari karne wale chhatron ke liye saste aur surakshit hostel uplabdh karaye jayenge.",
        "dialogue": "Main jaanti hoon sapne bade hote hain, par sahare chhote pad jaate hain. Isliye har mehanati bachche ko padhai ke liye surakshit aur sasta rehne ka adhikar milega. Taiyari ab paise walon tak simit nahi rahegi.",
        "speech_style": "compassionate",
        "target_group_id": 1,
        "shift_amount": 4.5,
        "archetype_suitability": "mukti_devi",
        "used_by": None
    },
    {
        "id": 225,
        "title": "Digital Freelancer Bharat Mission",
        "description": "Yuva tech professionals ko freelancing, remote jobs aur global contracts ke liye training aur legal support diya jayega.",
        "dialogue": "Duniya badal chuki hai, kaam ab shehar ki deewar se bandha nahi hai. Main chahta hoon hamare yuva duniya bhar ke clients ke saath kaam karein aur apne ghar se kamayen. Talent ko ab border nahi rokega.",
        "speech_style": "visionary",
        "target_group_id": 2,
        "shift_amount": 4.8,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 226,
        "title": "Mazdoor Pension Nyay Yojana",
        "description": "Asangathit kshetra ke vriddh mazdooron ke liye minimum monthly pension aur swasthya sahayata sunischit ki jayegi.",
        "dialogue": "Jinhone apni jawani desh banane mein laga di, unka budhaapa besahara nahi hoga. Main vriddh mazdooron ko samman aur suraksha ke saath jeene ka adhikar dilakar rahungi. Yeh daya nahi, nyay hai.",
        "speech_style": "emotional",
        "target_group_id": 3,
        "shift_amount": 4.7,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 227,
        "title": "Yuva Civic Leadership Camps",
        "description": "Rajneeti, samaj seva aur leadership seekhne ke liye college aur zila star par youth leadership camps chalaye jayenge.",
        "dialogue": "Desh ko sirf naukri karne wale yuva nahi, netritva karne wale yuva bhi chahiye. Main chahta hoon har yuva samvidhan, samaj aur zimmedari ko samjhe. Kal ka neta aaj ke campus se niklega.",
        "speech_style": "inspirational",
        "target_group_id": 4,
        "shift_amount": 2.8,
        "archetype_suitability": "all",
        "used_by": None
    },
    {
        "id": 228,
        "title": "Kisan Drone Sahayata Kendra",
        "description": "Badi lagat ke bina kheti mein spray, survey aur monitoring ke liye shared agriculture drone seva shuru ki jayegi.",
        "dialogue": "Hamare kisan ko purani mushkilein aur nayi technology dono ka bojh akela nahi uthana padega. Main kheti ko tez, sasti aur samajhdaar banane ke liye drone seva gaon tak launga. Ab kheti bhi future-ready hogi.",
        "speech_style": "visionary",
        "target_group_id": 0,
        "shift_amount": 4.1,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 229,
        "title": "Sanskriti Pathshala Network",
        "description": "Bachchon aur yuvaon ko itihaas, granth, kala aur sanskritik moolyon se jodne ke liye shaam ki pathshala chalayi jayegi.",
        "dialogue": "Jo apni jadon se juda hota hai wahi mazboot bhavishya banata hai. Hamare bachche adhunik bhi banenge aur apni parampara se jude bhi rahenge. Sanskriti hi samaj ki aatma hoti hai.",
        "speech_style": "nationalist",
        "target_group_id": 1,
        "shift_amount": 3.3,
        "archetype_suitability": "dharma_rakshak",
        "used_by": None
    },
    {
        "id": 230,
        "title": "Rural Electronics Manufacturing Park",
        "description": "Chhote shahron mein electronics assembly aur repair clusters sthapit kar local rojgar aur industry ko badhava diya jayega.",
        "dialogue": "Rozgar ke liye yuva ko ghar chhodna majboori nahi rehni chahiye. Main industry ko chhote shahron tak launga aur local talent ko local mauka dunga. Vikas tabhi sach hoga jab har zila aage badhega.",
        "speech_style": "visionary",
        "target_group_id": 2,
        "shift_amount": 4.6,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 231,
        "title": "Shramik Nyay Helpline",
        "description": "Mazdooron ke vetan, durghatna, shoshan aur kaam ki sharten sambandhi shikayaton ke liye 24x7 kanooni madad helpline shuru ki jayegi.",
        "dialogue": "Mazdoor ki awaaz dabayi nahi jayegi, suni jayegi. Main har shoshan ke khilaf kanooni sahara aur turant madad dene ka pran leti hoon. Ab mazdoor akela nahi padega.",
        "speech_style": "aggressive",
        "target_group_id": 3,
        "shift_amount": 3.5,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 232,
        "title": "Night Study and Skill Cafes",
        "description": "Yuvaon ke liye raat tak khule rehne wale study, internet aur skill practice spaces har bade kasbe mein banaye jayenge.",
        "dialogue": "Har sapna 9 se 5 ke beech paida nahi hota. Bahut se yuva raat mein padhte hain, seekhte hain, khud ko banaate hain. Main unke liye jagah, suvidha aur ek naya mahaul dunga.",
        "speech_style": "inspirational",
        "target_group_id": 4,
        "shift_amount": 3.9,
        "archetype_suitability": "all",
        "used_by": None
    },
    {
        "id": 233,
        "title": "Zero Byaj Kisan Rin Sahayata",
        "description": "Samay par bhugtan karne wale chhote aur seemant kisanon ko zero-interest crop loan uplabdh karaya jayega.",
        "dialogue": "Kisan fasal ugaye ya byaj chukaye — yeh chunav uske saamne nahi hona chahiye. Main kisan ko karz ke bojh se rahat aur mehnat ka sahara dunga. Kheti ko dabav nahi, dum chahiye.",
        "speech_style": "grassroots",
        "target_group_id": 0,
        "shift_amount": 4.4,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 234,
        "title": "Merit to Mission Scholarship",
        "description": "Ucch ank laane wale aur arthik roop se kamzor chhatron ko graduation aur professional courses ke liye poori sahayata di jayegi.",
        "dialogue": "Main chahti hoon ki mehnat ka inaam paisa nahi, pratibha tay kare. Har yogya bachche ko uski padhai aur uske sapne tak pahunchne ka pura mauka diya jayega. Hunar kisi ek ghar ki jaagir nahi hai.",
        "speech_style": "inspirational",
        "target_group_id": 1,
        "shift_amount": 4.3,
        "archetype_suitability": "mukti_devi",
        "used_by": None
    },
    {
        "id": 235,
        "title": "Bharat Cloud Skill Card",
        "description": "Cloud, cybersecurity, data aur AI skills mein certification ke liye yuva professionals ko subsidized vouchers diye jayenge.",
        "dialogue": "Aane wale daur ki ladai sirf naukri ki nahi, skill ki hai. Main chahta hoon hamare yuva global level ki technology seekhein aur duniya se takkar lein. Bharat ka talent duniya par chha sakta hai.",
        "speech_style": "visionary",
        "target_group_id": 2,
        "shift_amount": 3.7,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 236,
        "title": "Mazdoor Mobile Clinic Vans",
        "description": "Nirman sthal, karkhano aur bastiyon mein mobile health vans bhejkar mazdooron ko free ilaaj aur jaanch di jayegi.",
        "dialogue": "Jo mazdoor din-raat mehnat karta hai, usse ilaaj ke liye line mein tadapna nahi chahiye. Main sehat ko uske paas le jaungi, use bhatakne nahi dungi. Sehat bhi adhikar hai, suvidha nahi.",
        "speech_style": "compassionate",
        "target_group_id": 3,
        "shift_amount": 4.0,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 237,
        "title": "Yuva Sansad Fellowship",
        "description": "Desh, samvidhan aur niti nirman ko samajhne ke liye yuvaon ke liye legislative fellowship aur policy workshops chalayi jayengi.",
        "dialogue": "Main chahti hoon ki yuva sirf vote na dein, desh ki niti bhi samjhein. Unhe samvidhan, sansad aur shasan ki prakriya ka hissa banana zaroori hai. Nayi soch se hi naya rashtra banta hai.",
        "speech_style": "reformist",
        "target_group_id": 4,
        "shift_amount": 2.7,
        "archetype_suitability": "all",
        "used_by": None
    },
    {
        "id": 238,
        "title": "Organic Gram Cluster Scheme",
        "description": "Chuninda gaonon ko organic kheti clusters ke roop mein vikasit karke premium bazaar se joda jayega.",
        "dialogue": "Dharti maa ko bachakar hi kheti ka bhavishya surakshit hoga. Main hamare gaon ko prakritik kheti aur behtar bazaar dono se jodunga. Parampara aur pragati saath-saath chal sakte hain.",
        "speech_style": "nationalist",
        "target_group_id": 0,
        "shift_amount": 3.2,
        "archetype_suitability": "dharma_rakshak",
        "used_by": None
    },
    {
        "id": 239,
        "title": "Career Saathi Counseling Bus",
        "description": "School aur college chhatron ke liye gaon-gaon ghoomkar career guidance, aptitude test aur admission madad di jayegi.",
        "dialogue": "Main chahti hoon ki gaon ka bachcha bhi wahi jaankari paaye jo bade shehar ka bachcha paata hai. Career ki sahi disha har ghar tak pahunchni chahiye. Sapne tabhi sach hote hain jab raasta bhi dikhai de.",
        "speech_style": "compassionate",
        "target_group_id": 1,
        "shift_amount": 3.8,
        "archetype_suitability": "mukti_devi",
        "used_by": None
    },
    {
        "id": 240,
        "title": "Tech Seva Bharat Corps",
        "description": "Trained digital volunteers ke madhyam se gaon aur kasbon mein online forms, e-governance aur digital sevaon ki madad pahunchayi jayegi.",
        "dialogue": "Digital Bharat tabhi safal hoga jab gaon ka aam nagrik bhi bina dare system ka istemal kar sake. Main technology ko jan seva ka hathiyar banaunga. Suvidha har haath tak pahunchni chahiye.",
        "speech_style": "grassroots",
        "target_group_id": 2,
        "shift_amount": 2.6,
        "archetype_suitability": "all",
        "used_by": None
    }
]

def get_available_manifestos(db, session_id):
    """Returns only manifestos that haven't been claimed yet for this session."""
    return list(db.manifestos.find({"session_id": session_id, "used_by": None}, {"_id": 0}))

def get_all_manifestos(db, session_id):
    """Returns all manifestos for this session with their used_by status."""
    return list(db.manifestos.find({"session_id": session_id}, {"_id": 0}))

def claim_manifesto(db, manifesto_id, candidate_id, session_id):
    """Marks a manifesto as used by a specific candidate for this session."""
    m = db.manifestos.find_one_and_update(
        {"session_id": session_id, "id": manifesto_id, "used_by": None},
        {"$set": {"used_by": candidate_id}},
        return_document=True
    )
    if m:
        m_copy = dict(m)
        m_copy.pop('_id', None)
        return m_copy
    return None