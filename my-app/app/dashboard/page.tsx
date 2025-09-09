"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Globe, LogOut, Plus, Sparkles, Search, X } from "lucide-react"
import { useAuth } from "@/lib/auth-context"

export default function BrandProfilePage() {
  const [brandData, setBrandData] = useState({
    companyName: "",
    website: "",
    keywords: [] as string[],
  })
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([])
  const [newKeyword, setNewKeyword] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [influencerResults, setInfluencerResults] = useState<any[]>([])
  const [averages, setAverages] = useState({ avg_views: 0, avg_score: 0 })
  
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
      const keywords = user.keywords ? user.keywords.split(',').map(k => k.trim()).filter(k => k) : []
      setBrandData({
        companyName: user.company_name || "",
        website: user.website || "",
        keywords: keywords,
      })
      setSelectedKeywords(keywords)
    }
  }, [user])

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!user) {
    return null
  }


  const handleSave = async () => {
    try {
      await updateProfile({
        company_name: brandData.companyName,
        website: brandData.website,
        keywords: selectedKeywords.join(', '),
      })
      alert("Profile updated successfully!")
    } catch (error) {
      console.error("Failed to update profile:", error)
      alert("Failed to update profile. Please try again.")
    }
  }

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !brandData.keywords.includes(newKeyword.trim())) {
      const updatedKeywords = [...brandData.keywords, newKeyword.trim()]
      setBrandData(prev => ({ ...prev, keywords: updatedKeywords }))
      setNewKeyword("")
    }
  }

  const handleRemoveKeyword = (keyword: string) => {
    const updatedKeywords = brandData.keywords.filter(k => k !== keyword)
    setBrandData(prev => ({ ...prev, keywords: updatedKeywords }))
    setSelectedKeywords(prev => prev.filter(k => k !== keyword))
  }

  const handleGenerateKeywords = async () => {
    if (!brandData.website) {
      alert("Please enter a website URL first")
      return
    }

    setIsGenerating(true)
    try {
      // Call the backend to generate keywords from website
      const response = await fetch('http://localhost:5000/api/auth/generate-keywords', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ website: brandData.website }),
      })

      if (response.ok) {
        const data = await response.json()
        const generatedKeywords = data.keywords || []
        
        // Add new keywords to existing ones (avoid duplicates)
        setBrandData(prev => {
          const existingKeywords = prev.keywords || []
          const newKeywords = generatedKeywords.filter(keyword => 
            !existingKeywords.includes(keyword)
          )
          const updatedKeywords = [...existingKeywords, ...newKeywords]
          return { ...prev, keywords: updatedKeywords }
        })
        
        // Add new keywords to selected keywords as well
        setSelectedKeywords(prev => {
          const existingSelected = prev || []
          const newKeywords = generatedKeywords.filter(keyword => 
            !existingSelected.includes(keyword)
          )
          return [...existingSelected, ...newKeywords]
        })
        
        alert(`Generated ${generatedKeywords.length} new keywords from your website!`)
      } else {
        throw new Error('Failed to generate keywords')
      }
    } catch (error) {
      console.error("Failed to generate keywords:", error)
      alert("Failed to generate keywords. Please try again.")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSearchInfluencers = async () => {
    if (selectedKeywords.length === 0) {
      alert("Please select at least one keyword to search for influencers")
      return
    }

    setIsSearching(true)
    try {
      // Call the backend to search for influencers
      const response = await fetch('http://localhost:5000/api/auth/search-influencers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keywords: selectedKeywords }),
      })

      if (response.ok) {
        const data = await response.json()
        setInfluencerResults(data.influencers || [])
        setAverages(data.averages || { avg_views: 0, avg_score: 0 })
        alert(`Found ${data.count || 0} influencers! Results displayed on the right.`)
      } else {
        throw new Error('Failed to search for influencers')
      }
    } catch (error) {
      console.error("Failed to search for influencers:", error)
      alert("Failed to search for influencers. Please try again.")
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeywordToggle = (keyword: string, checked: boolean) => {
    if (checked) {
      setSelectedKeywords(prev => [...prev, keyword])
    } else {
      setSelectedKeywords(prev => prev.filter(k => k !== keyword))
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
            Welcome back, {user.company_name || user.email}! Manage your brand information for better influencer matching
          </p>
        </div>
        <div className="flex items-center space-x-2">
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

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="keywords">Company Keywords</Label>
                  <div className="flex space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleGenerateKeywords}
                      disabled={isGenerating || !brandData.website}
                    >
                      <Sparkles className="w-4 h-4 mr-2" />
                      {isGenerating ? "Generating..." : "Generate"}
                    </Button>
                  </div>
                </div>

                {/* Add new keyword */}
                <div className="flex space-x-2">
                  <Input
                    placeholder="Add a keyword..."
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleAddKeyword}
                    disabled={!newKeyword.trim()}
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>

                {/* Keywords list with checkboxes */}
                {brandData.keywords.length > 0 ? (
                  <div className="space-y-2">
                    <Label className="text-sm text-muted-foreground">Select keywords for influencer search:</Label>
                    <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto border rounded-md p-3">
                      {brandData.keywords.map((keyword, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Checkbox
                            id={`keyword-${index}`}
                            checked={selectedKeywords.includes(keyword)}
                            onCheckedChange={(checked) => handleKeywordToggle(keyword, checked as boolean)}
                          />
                          <Label
                            htmlFor={`keyword-${index}`}
                            className="flex-1 text-sm cursor-pointer"
                          >
                            {keyword}
                          </Label>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveKeyword(keyword)}
                            className="h-6 w-6 p-0"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No keywords yet. Add some manually or generate them from your website.</p>
                  </div>
                )}

                {/* Selected keywords summary */}
                {selectedKeywords.length > 0 && (
                  <div className="space-y-2">
                    <Label className="text-sm text-muted-foreground">Selected for search:</Label>
                    <div className="flex flex-wrap gap-2">
                      {selectedKeywords.map((keyword, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Search and Save buttons */}
                <div className="flex space-x-2">
                  <Button
                    onClick={handleSearchInfluencers}
                    disabled={isSearching || selectedKeywords.length === 0}
                    className="flex-1"
                  >
                    <Search className="w-4 h-4 mr-2" />
                    {isSearching ? "Searching..." : "Search Influencers"}
                  </Button>
                  <Button onClick={handleSave} variant="outline">
                    Save Changes
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Influencer Results */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Influencer Search Results</CardTitle>
              <CardDescription>
                {influencerResults.length > 0 
                  ? `Found ${influencerResults.length} influencers with pricing estimates`
                  : "Search for influencers using your selected keywords"
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              {influencerResults.length > 0 ? (
                <div className="space-y-4">
                  {/* Averages */}
                  <div className="grid grid-cols-2 gap-4 p-4 bg-muted rounded-lg">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {Math.round(averages.avg_views).toLocaleString()}
                      </div>
                      <div className="text-sm text-muted-foreground">Avg Views</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {averages.avg_score.toFixed(1)}
                      </div>
                      <div className="text-sm text-muted-foreground">Avg Score</div>
                    </div>
                  </div>

                  {/* Influencer List */}
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {influencerResults.map((influencer) => (
                      <div key={influencer.id} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                        {influencer.url ? (
                          <a 
                            href={influencer.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="block cursor-pointer"
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h3 className="font-semibold text-sm hover:text-primary transition-colors">{influencer.title}</h3>
                                <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                                  <span>👥 {influencer.subs}</span>
                                  <span>👁️ {influencer.views}</span>
                                  <span>⭐ {influencer.score}</span>
                                </div>
                                {influencer.description && (
                                  <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                                    {influencer.description}
                                  </p>
                                )}
                              </div>
                              <div className="text-right">
                                <div className="text-lg font-bold text-green-600">
                                  {influencer.pricing}
                                </div>
                                <div className="text-xs text-muted-foreground">Sponsorship</div>
                              </div>
                            </div>
                            <div className="text-xs text-blue-600 hover:underline mt-2 inline-block">
                              View Channel →
                            </div>
                          </a>
                        ) : (
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="font-semibold text-sm">{influencer.title}</h3>
                              <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                                <span>👥 {influencer.subs}</span>
                                <span>👁️ {influencer.views}</span>
                                <span>⭐ {influencer.score}</span>
                              </div>
                              {influencer.description && (
                                <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                                  {influencer.description}
                                </p>
                              )}
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-green-600">
                                {influencer.pricing}
                              </div>
                              <div className="text-xs text-muted-foreground">Sponsorship</div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <div className="text-4xl mb-4">🔍</div>
                  <p>No influencers found yet.</p>
                  <p className="text-sm">Select keywords and click "Search Influencers" to get started.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
