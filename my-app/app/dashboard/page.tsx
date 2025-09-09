"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Globe, RefreshCw, CheckCircle, AlertCircle, TrendingUp, Users, Target, Palette, LogOut } from "lucide-react"
import { useAuth } from "@/lib/auth-context"

export default function BrandProfilePage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [brandData, setBrandData] = useState({
    companyName: "",
    website: "",
    industry: "",
    description: "",
    targetAudience: "",
    brandValues: "",
  })
  
  const { user, isLoading, logout, updateProfile } = useAuth()
  const router = useRouter()

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  // Initialize brand data from user profile
  useEffect(() => {
    if (user) {
      setBrandData({
        companyName: user.company_name || "",
        website: user.website || "",
        industry: "",
        description: "",
        targetAudience: "",
        brandValues: "",
      })
    }
  }, [user])

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!user) {
    return null
  }

  // Mock website analysis data
  const websiteAnalysis = {
    status: "completed",
    lastAnalyzed: "2024-01-15",
    insights: {
      brandTone: "Professional, Modern, Tech-savvy",
      primaryColors: ["#1f2937", "#3b82f6", "#ffffff"],
      keyTopics: ["Software Development", "Business Automation", "Productivity Tools", "Enterprise Solutions"],
      targetDemographics: ["25-45 years", "Business professionals", "Tech industry"],
      contentThemes: ["Innovation", "Efficiency", "Digital Transformation", "Business Growth"],
    },
    metrics: {
      analysisScore: 92,
      brandClarity: 88,
      contentQuality: 95,
      targetAlignment: 89,
    },
  }

  const handleAnalyzeWebsite = () => {
    setIsAnalyzing(true)
    // Simulate analysis
    setTimeout(() => {
      setIsAnalyzing(false)
    }, 3000)
  }

  const handleSave = async () => {
    try {
      await updateProfile({
        company_name: brandData.companyName,
        website: brandData.website,
      })
      // Show success message or toast
    } catch (error) {
      console.error("Failed to update profile:", error)
    }
  }

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Brand Profile</h1>
          <p className="text-muted-foreground">
            Welcome back, {user.company_name || user.email}! Manage your brand information and analyze your website for better influencer matching
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={handleAnalyzeWebsite} disabled={isAnalyzing}>
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                Re-analyze Website
              </>
            )}
          </Button>
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Brand Information Form */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
              <CardDescription>Update your brand details to improve influencer matching accuracy</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="companyName">Company Name</Label>
                <Input
                  id="companyName"
                  value={brandData.companyName}
                  onChange={(e) => setBrandData((prev) => ({ ...prev, companyName: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="website">Website URL</Label>
                <div className="flex space-x-2">
                  <Input
                    id="website"
                    value={brandData.website}
                    onChange={(e) => setBrandData((prev) => ({ ...prev, website: e.target.value }))}
                  />
                  <Button variant="outline" size="icon">
                    <Globe className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="industry">Industry</Label>
                <Input
                  id="industry"
                  value={brandData.industry}
                  onChange={(e) => setBrandData((prev) => ({ ...prev, industry: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Company Description</Label>
                <Textarea
                  id="description"
                  value={brandData.description}
                  onChange={(e) => setBrandData((prev) => ({ ...prev, description: e.target.value }))}
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="targetAudience">Target Audience</Label>
                <Textarea
                  id="targetAudience"
                  value={brandData.targetAudience}
                  onChange={(e) => setBrandData((prev) => ({ ...prev, targetAudience: e.target.value }))}
                  rows={2}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="brandValues">Brand Values</Label>
                <Input
                  id="brandValues"
                  value={brandData.brandValues}
                  onChange={(e) => setBrandData((prev) => ({ ...prev, brandValues: e.target.value }))}
                  placeholder="Separate with commas"
                />
              </div>

              <Button onClick={handleSave} className="w-full">
                Save Changes
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Website Analysis Results */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Website Analysis</CardTitle>
                  <CardDescription>AI-powered insights from your website content</CardDescription>
                </div>
                {websiteAnalysis.status === "completed" ? (
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Completed
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Pending
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Analysis Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Analysis Score</span>
                    <span className="font-medium">{websiteAnalysis.metrics.analysisScore}%</span>
                  </div>
                  <Progress value={websiteAnalysis.metrics.analysisScore} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Brand Clarity</span>
                    <span className="font-medium">{websiteAnalysis.metrics.brandClarity}%</span>
                  </div>
                  <Progress value={websiteAnalysis.metrics.brandClarity} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Content Quality</span>
                    <span className="font-medium">{websiteAnalysis.metrics.contentQuality}%</span>
                  </div>
                  <Progress value={websiteAnalysis.metrics.contentQuality} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Target Alignment</span>
                    <span className="font-medium">{websiteAnalysis.metrics.targetAlignment}%</span>
                  </div>
                  <Progress value={websiteAnalysis.metrics.targetAlignment} className="h-2" />
                </div>
              </div>

              {/* Brand Insights */}
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Palette className="w-5 h-5 text-accent" />
                  <h4 className="font-semibold">Brand Tone</h4>
                </div>
                <p className="text-sm text-muted-foreground pl-7">{websiteAnalysis.insights.brandTone}</p>

                <div className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-accent" />
                  <h4 className="font-semibold">Key Topics</h4>
                </div>
                <div className="flex flex-wrap gap-2 pl-7">
                  {websiteAnalysis.insights.keyTopics.map((topic, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {topic}
                    </Badge>
                  ))}
                </div>

                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-accent" />
                  <h4 className="font-semibold">Target Demographics</h4>
                </div>
                <div className="flex flex-wrap gap-2 pl-7">
                  {websiteAnalysis.insights.targetDemographics.map((demo, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {demo}
                    </Badge>
                  ))}
                </div>

                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5 text-accent" />
                  <h4 className="font-semibold">Content Themes</h4>
                </div>
                <div className="flex flex-wrap gap-2 pl-7">
                  {websiteAnalysis.insights.contentThemes.map((theme, index) => (
                    <Badge key={index} variant="outline" className="text-xs bg-accent/10 text-accent border-accent/20">
                      {theme}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="text-xs text-muted-foreground pt-4 border-t border-border">
                Last analyzed: {websiteAnalysis.lastAnalyzed}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
