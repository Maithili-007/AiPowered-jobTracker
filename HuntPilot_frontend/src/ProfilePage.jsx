import ProfileResumeUpload from './ProfileResumeUpload';

export default function ProfilePage() {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="card shadow-lg">
          {/* Header */}
          <div className="bg-primary text-white p-6">
            <h4 className="font-bold text-2xl">Your Profile</h4>
          </div>

          {/* Body */}
          <div className="p-6">
            <p className="text-gray-700 mb-6">
              Upload your resume once, and we'll use it to match you against every new job you add.
            </p>

            {/* Resume Upload Section */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <ProfileResumeUpload />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
