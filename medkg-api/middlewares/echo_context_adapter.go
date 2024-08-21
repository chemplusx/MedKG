package middlewares

import (
	"io"
	"mime/multipart"
	"net/http"
	"net/url"

	"github.com/gin-gonic/gin"
	"github.com/labstack/echo/v4"
)

type echoContextAdapter struct {
	c *gin.Context
}

func (e *echoContextAdapter) Reset(r *http.Request, w http.ResponseWriter) {}

func (e *echoContextAdapter) Request() *http.Request {
	return e.c.Request
}

func (e *echoContextAdapter) Response() *echo.Response {
	return nil // Implement if needed
}

func (e *echoContextAdapter) Echo() *echo.Echo {
	return nil // Implement if needed
}

func (e *echoContextAdapter) SetRequest(r *http.Request) {}

func (e *echoContextAdapter) SetResponse(w *echo.Response) {}

func (e *echoContextAdapter) Path() string {
	return e.c.FullPath()
}

func (e *echoContextAdapter) Param(name string) string {
	return e.c.Param(name)
}

func (e *echoContextAdapter) ParamNames() []string {
	return nil // Implement if needed
}

func (e *echoContextAdapter) ParamValues() []string {
	return nil // Implement if needed
}

func (e *echoContextAdapter) QueryParam(name string) string {
	return e.c.Query(name)
}

func (e *echoContextAdapter) QueryParams() map[string][]string {
	return e.c.Request.URL.Query()
}

func (e *echoContextAdapter) QueryString() string {
	return e.c.Request.URL.RawQuery
}

func (e *echoContextAdapter) FormValue(name string) string {
	return e.c.Request.FormValue(name)
}

func (e *echoContextAdapter) FormParams() (url.Values, error) {
	return nil, nil // Implement if needed
}

func (e *echoContextAdapter) FormFile(name string) (*multipart.FileHeader, error) {
	return nil, nil // Implement if needed
}

func (e *echoContextAdapter) MultipartForm() (*multipart.Form, error) {
	return nil, nil // Implement if needed
}

func (e *echoContextAdapter) Cookie(name string) (*http.Cookie, error) {
	return e.c.Request.Cookie(name)
}

func (e *echoContextAdapter) SetCookie(cookie *http.Cookie) {
	http.SetCookie(e.c.Writer, cookie)
}

func (e *echoContextAdapter) Cookies() []*http.Cookie {
	return e.c.Request.Cookies()
}

func (e *echoContextAdapter) Get(key string) (interface{}, bool) {
	return e.c.Get(key)
}

func (e *echoContextAdapter) Set(key string, val interface{}) {
	e.c.Set(key, val)
}

func (e *echoContextAdapter) Bind(i interface{}) error {
	return e.c.ShouldBind(i)
}

func (e *echoContextAdapter) Validate(i interface{}) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) Render(code int, name string, data interface{}) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) HTML(code int, html string) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) String(code int, s string) error {
	e.c.String(code, s)
	return nil
}

func (e *echoContextAdapter) JSON(code int, i interface{}) error {
	e.c.JSON(code, i)
	return nil
}

func (e *echoContextAdapter) JSONPretty(code int, i interface{}, indent string) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) JSONBlob(code int, b []byte) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) JSONP(code int, callback string, i interface{}) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) XML(code int, i interface{}) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) XMLPretty(code int, i interface{}, indent string) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) XMLBlob(code int, b []byte) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) Blob(code int, contentType string, b []byte) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) Stream(code int, contentType string, r io.Reader) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) File(file string) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) Attachment(file, name string) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) Inline(file, name string) error {
	return nil // Implement if needed
}

func (e *echoContextAdapter) NoContent(code int) error {
	e.c.Status(code)
	return nil
}

func (e *echoContextAdapter) Redirect(code int, url string) error {
	e.c.Redirect(code, url)
	return nil
}

func (e *echoContextAdapter) Error(err error) {
	e.c.Error(err)
}
