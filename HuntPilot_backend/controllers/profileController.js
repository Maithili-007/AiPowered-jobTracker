const User = require('../models/User');
const fs = require('fs');
const axios = require('axios');
const pdfParse = require('pdf-parse');
const fsPromises = fs.promises;

exports.uploadResume = async (req,res,next)=>{
try{
const userId = req.user.id;
const { path: filePath, mimetype, originalname } = req.file;
const dataBuffer = fs.readFileSync(filePath);
let text;
    if (mimetype === 'application/pdf') {
      // PDF: use pdf-parse
      const parsed = await pdfParse(dataBuffer);
      text = parsed.text;
    } else if (mimetype.startsWith('text/')) {
      // Plain text: convert buffer to string
      text = dataBuffer.toString('utf8');
    } else {
      // Unsupported type
      return res.status(400).json({ error: 'Only PDF or plain-text resumes are supported' });
    }

const {data} =  await axios.post('https://aipowered-jobtracker-1.onrender.com/extract-keywords',{description:text});

// Remove old resume if exists
const oldUser = await User.findById(userId);
    if (oldUser.resumePath) {
  try {
    await fsPromises.unlink(oldUser.resumePath);
  } catch (err) {
    if (err.code !== 'ENOENT') console.error("Error deleting old resume:", err);
  }
}

await User.findByIdAndUpdate(userId,{
  resumeKeywords:data.keywords,
  resumeFilename:req.file.originalname,
   resumePath: filePath   
  });
  res.json({message:'Resume uploaded and keywords updated', keywords:data.keywords,resumeFilename: originalname });
}
  catch(error){
 console.error(error);
    res.status(500).json({ error: 'Failed to upload or parse resume' });
  }
};

exports.getResume = async(req,res,next)=>{
try{
  const userId = req.user.id;
  const user = await User.findById(userId);
  res.json({
    resumeFilename:user.resumeFilename || '',
    resumeKeywords:user.resumeKeywords || [],
  });
}
catch (error) {
    res.status(500).json({ error: 'Failed to fetch resume info' });
  }
};

exports.deleteResume = async (req, res) => {
  try{
    const userId = req.user.id;
    const user = await User.findById(userId);

    if (user.resumePath) {
  try {
    await fsPromises.unlink(user.resumePath);
  } catch (err) {
    if (err.code !== 'ENOENT') console.error("Error deleting file:", err);
  }
}

    await User.findByIdAndUpdate(userId,{
      $unset: {
        resumeKeywords: '',
        resumeFilename: '',
        resumePath: '',
      },
    });
    res.json({ message: 'Resume deleted successfully' });
  }
  catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to delete resume' });
  }
};

exports.downloadResume = async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    if (!user.resumePath) {
      return res.status(404).json({ error: 'No resume uploaded' });
    }
    // Send file back with original filename
    res.download(user.resumePath, user.resumeFilename);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to download resume' });
  }
};
